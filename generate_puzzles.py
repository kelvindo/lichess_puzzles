import csv
import random
from process_puzzles import Puzzle
from typing import Dict, List


PUZZLES_OPENING = "Opening"
PUZZLES_MIDDLEGAME = "Middlegame"
PUZZLES_ENDGAME = "Endgame"
PUZZLES_MIXED = "Mixed"

PUZZLE_FILES = {
    PUZZLES_OPENING: "puzzles/opening.csv",
    PUZZLES_MIDDLEGAME: "puzzles/middlegame.csv",
    PUZZLES_ENDGAME: "puzzles/endgame.csv",
}


def coin_flip() -> bool:
    return random.random() > 0.5


class PuzzleGenerator:
    def __init__(self):
        self.puzzle_mapping = self.load_puzzles()

    def load_puzzles(self) -> Dict[str, List[Puzzle]]:
        puzzle_mapping: Dict[str, List[Puzzle]] = {
            PUZZLES_OPENING: [],
            PUZZLES_MIDDLEGAME: [],
            PUZZLES_ENDGAME: [],
            PUZZLES_MIXED: [],
        }
        for name, file_name in PUZZLE_FILES.items():
            with open(file_name, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    puzzle = Puzzle.from_dict(row)
                    puzzle_mapping[name].append(puzzle)

        puzzle_mapping[PUZZLES_MIXED] = (
            puzzle_mapping[PUZZLES_OPENING]
            + puzzle_mapping[PUZZLES_MIDDLEGAME]
            + puzzle_mapping[PUZZLES_ENDGAME]
        )

        return puzzle_mapping

    def generate_puzzle_pack_pgn_strings(
        self,
        puzzle_pack_name: str,
        num_puzzles: int = 32,
    ) -> List[str]:
        pgn_strings = []
        for puzzle in random.sample(self.puzzle_mapping[puzzle_pack_name], num_puzzles):
            fen = puzzle.generate_puzzle_position(coin_flip())
            pgn_strings.append(
                f'[FEN "{fen}"]\n[SITE "https://lichess.org/training/{puzzle.puzzle_id}"]\n\n*\n\n'
            )
        return pgn_strings
