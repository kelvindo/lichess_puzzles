import csv
import random
from process_puzzles import Puzzle
from typing import Dict, List


PUZZLES_OPENING = "Opening"
PUZZLES_MIDDLEGAME = "Middlegame"
PUZZLES_ENDGAME = "Endgame"
PUZZLES_RANDOM = "Random"

PUZZLE_FILES = {
    PUZZLES_OPENING: "puzzles/opening.csv",
    PUZZLES_MIDDLEGAME: "puzzles/middlegame.csv",
    PUZZLES_ENDGAME: "puzzles/endgame.csv",
}

NUM_OPENINGS = 256
RATING_SAMPLE_SIZE = 1000


def coin_flip() -> bool:
    return random.random() > 0.5


class PuzzleGenerator:
    def __init__(self):
        self.puzzle_mapping = self.load_puzzles()
        self.opening_puzzle_mapping = self.load_opening_puzzles()

    def load_puzzles(self) -> Dict[str, List[Puzzle]]:
        puzzle_mapping: Dict[str, List[Puzzle]] = {
            PUZZLES_OPENING: [],
            PUZZLES_MIDDLEGAME: [],
            PUZZLES_ENDGAME: [],
            PUZZLES_RANDOM: [],
        }
        for name, file_name in PUZZLE_FILES.items():
            with open(file_name, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    puzzle = Puzzle.from_dict(row)
                    puzzle_mapping[name].append(puzzle)

        puzzle_mapping[PUZZLES_RANDOM] = (
            puzzle_mapping[PUZZLES_OPENING]
            + puzzle_mapping[PUZZLES_MIDDLEGAME]
            + puzzle_mapping[PUZZLES_ENDGAME]
        )

        return puzzle_mapping

    def load_opening_puzzles(self) -> Dict[str, List[Puzzle]]:
        opening_puzzle_mapping: Dict[str, List[Puzzle]] = {}
        with open("puzzles/opening_tag.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                puzzle = Puzzle.from_dict(row)
                for tag in puzzle.opening_tags.split(" "):
                    if not tag.strip():
                        continue
                    display_tag = convert_to_display(tag)
                    opening_puzzle_mapping.setdefault(display_tag, []).append(puzzle)

        # Filter to the top NUM_OPENINGS openings.
        opening_puzzle_mapping = {
            k: v
            for k, v in sorted(
                opening_puzzle_mapping.items(), key=lambda x: len(x[1]), reverse=True
            )[:NUM_OPENINGS]
        }

        # Sort the openings by name.
        opening_puzzle_mapping = {
            k: v
            for k, v in sorted(
                opening_puzzle_mapping.items(), key=lambda x: x[0], reverse=False
            )
        }

        return opening_puzzle_mapping

    def get_puzzle_pack_names(self) -> List[str]:
        puzzle_packs = [
            PUZZLES_RANDOM,
            PUZZLES_OPENING,
            PUZZLES_MIDDLEGAME,
            PUZZLES_ENDGAME,
        ]

        puzzle_packs.extend(self.opening_puzzle_mapping.keys())
        return puzzle_packs

    def generate_puzzle_pack_pgn_strings(
        self,
        puzzle_pack_name: str,
        num_puzzles: int,
        target_rating: int,
    ) -> List[str]:
        pgn_strings = []
        puzzles = []
        if puzzle_pack_name in self.puzzle_mapping:
            puzzles = self.puzzle_mapping[puzzle_pack_name]
        elif puzzle_pack_name in self.opening_puzzle_mapping:
            puzzles = self.opening_puzzle_mapping[puzzle_pack_name]
        else:
            return ["Invalid puzzle pack name."]

        puzzles = target_puzzles_by_rating(puzzles, target_rating)

        for puzzle in random.sample(puzzles, min(len(puzzles), num_puzzles)):
            fen = puzzle.generate_puzzle_position(coin_flip())
            pgn_strings.append(
                f'[FEN "{fen}"]\n[SITE "https://lichess.org/training/{puzzle.puzzle_id}"]\n\n*\n\n'
            )
        return pgn_strings


def convert_to_display(opening: str) -> str:
    return " ".join([word.capitalize() for word in opening.split("_")])

def target_puzzles_by_rating(puzzles: List[Puzzle], target_rating: int):
    min_rating = target_rating - 100
    max_rating = target_rating + 100
    filtered_puzzles = [puzzle for puzzle in puzzles if puzzle.rating >= min_rating and puzzle.rating <= max_rating]

    if len(filtered_puzzles) >= RATING_SAMPLE_SIZE:
        return filtered_puzzles

    return sorted(puzzles, key=lambda x: abs(x.rating - target_rating))[:RATING_SAMPLE_SIZE]
