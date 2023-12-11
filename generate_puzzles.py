import csv
import random
import io
import chess.pgn
from process_puzzles import Puzzle
from typing import Dict, List, Tuple
import lichess.api
from lichess.format import PGN


PUZZLES_OPENING = "Opening"
PUZZLES_MIDDLEGAME = "Middlegame"
PUZZLES_ENDGAME = "Endgame"
PUZZLES_RANDOM = "Random"
PUZZLES_PERSONALIZED = "Personalized"

PUZZLE_FILES = {
    PUZZLES_OPENING: "puzzles/opening.csv",
    PUZZLES_MIDDLEGAME: "puzzles/middlegame.csv",
    PUZZLES_ENDGAME: "puzzles/endgame.csv",
}

NUM_OPENINGS = 256
MIN_PUZZLES_FOR_STRUCTURE = 5
RATING_SAMPLE_SIZE = 1000

LICHESS_USERNAME = "trisolaran3"
LICHESS_LAST_N_GAMES = 10


def coin_flip() -> bool:
    return random.random() > 0.5


class PuzzleGenerator:
    def __init__(self):
        self.puzzle_mapping = self.load_puzzles()
        # self.opening_puzzles_by_name = self.load_opening_puzzles_by_name()
        self.opening_puzzles_by_structure = self.load_opening_puzzles_by_structure()

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

    def load_opening_puzzles_by_name(self) -> Dict[str, List[Puzzle]]:
        opening_puzzles_by_name: Dict[str, List[Puzzle]] = {}
        with open("puzzles/opening_tag.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                puzzle = Puzzle.from_dict(row)
                for tag in puzzle.opening_tags.split(" "):
                    if not tag.strip():
                        continue
                    display_tag = convert_to_display(tag)
                    opening_puzzles_by_name.setdefault(display_tag, []).append(puzzle)

        # Filter to the top NUM_OPENINGS openings.
        opening_puzzles_by_name = {
            k: v
            for k, v in sorted(
                opening_puzzles_by_name.items(), key=lambda x: len(x[1]), reverse=True
            )[:NUM_OPENINGS]
        }

        # Sort the openings by name.
        opening_puzzles_by_name = {
            k: v
            for k, v in sorted(
                opening_puzzles_by_name.items(), key=lambda x: x[0], reverse=False
            )
        }

        return opening_puzzles_by_name

    def load_opening_puzzles_by_structure(self) -> Dict[str, List[Puzzle]]:
        opening_puzzles_by_structure: Dict[str, List[Puzzle]] = {}
        with open("puzzles/opening_tag.csv", "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                puzzle = Puzzle.from_dict(row)
                structure1 = pawns_only_fen(puzzle.fen)
                opening_puzzles_by_structure.setdefault(structure1, []).append(puzzle)

                structure2 = pawns_only_fen(
                    puzzle.generate_puzzle_position(defensive=False)
                )

                if structure1 == structure2:
                    continue

                opening_puzzles_by_structure.setdefault(structure2, []).append(puzzle)

        # Filter to structures with minimum number of puzzles.
        opening_puzzles_by_structure = {
            k: v
            for k, v in sorted(
                opening_puzzles_by_structure.items(),
                key=lambda x: len(x[1]),
                reverse=True,
            )
            if len(v) > MIN_PUZZLES_FOR_STRUCTURE
        }

        return opening_puzzles_by_structure

    def get_puzzle_pack_names(self) -> List[str]:
        puzzle_packs = [
            PUZZLES_RANDOM,
            PUZZLES_OPENING,
            PUZZLES_MIDDLEGAME,
            PUZZLES_ENDGAME,
            PUZZLES_PERSONALIZED,
        ]

        # puzzle_packs.extend(self.opening_puzzles_by_name.keys())
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
        elif puzzle_pack_name in self.opening_puzzles_by_name:
            puzzles = self.opening_puzzles_by_name[puzzle_pack_name]
        else:
            return ["Invalid puzzle pack name."]

        puzzles = target_puzzles_by_rating(puzzles, target_rating)

        for puzzle in random.sample(puzzles, min(len(puzzles), num_puzzles)):
            fen = puzzle.generate_puzzle_position(coin_flip())
            pgn_strings.append(
                f'[FEN "{fen}"]\n[SITE "https://lichess.org/training/{puzzle.puzzle_id}"]\n\n*\n\n'
            )
        return pgn_strings

    def get_personalized_puzzles(self) -> List[Puzzle]:
        structures = get_structure_sets_from_lichess(
            LICHESS_USERNAME, LICHESS_LAST_N_GAMES
        )

        puzzles: List[Puzzle] = []
        for structure in structures:
            matching_puzzles = self.opening_puzzles_by_structure.get(structure)
            if matching_puzzles:
                puzzles.extend(matching_puzzles)

        return puzzles

    def generate_puzzle_fen_string(
        self,
        puzzle_pack_name: str,
        target_rating: int,
    ) -> Tuple[str, str]:
        puzzles = []
        if puzzle_pack_name in self.puzzle_mapping:
            puzzles = self.puzzle_mapping[puzzle_pack_name]
        # elif puzzle_pack_name in self.opening_puzzles_by_name:
        #     puzzles = self.opening_puzzles_by_name[puzzle_pack_name]
        elif puzzle_pack_name == PUZZLES_PERSONALIZED:
            puzzles = self.get_personalized_puzzles()
        else:
            return ["Invalid puzzle pack name."]

        puzzles = target_puzzles_by_rating(puzzles, target_rating)

        puzzle = random.choice(puzzles)
        fen = puzzle.generate_puzzle_position(coin_flip())
        return fen, convert_to_analysis_url(fen)


def convert_to_display(opening: str) -> str:
    return " ".join([word.capitalize() for word in opening.split("_")])


def convert_to_analysis_url(fen: str) -> str:
    normalized_fen = fen.replace(" ", "_")
    return f"https://lichess.org/analysis/{normalized_fen}"


def target_puzzles_by_rating(puzzles: List[Puzzle], target_rating: int):
    min_rating = target_rating - 100
    max_rating = target_rating + 100
    filtered_puzzles = [
        puzzle
        for puzzle in puzzles
        if puzzle.rating >= min_rating and puzzle.rating <= max_rating
    ]

    if len(filtered_puzzles) >= RATING_SAMPLE_SIZE:
        return filtered_puzzles

    return sorted(puzzles, key=lambda x: abs(x.rating - target_rating))[
        :RATING_SAMPLE_SIZE
    ]


def extract_fens_from_pgn(pgn_string):
    # Parse the PGN string
    pgn = chess.pgn.read_game(io.StringIO(pgn_string))

    # List to store FENs
    fens = []

    # Iterate over all moves and save the FEN after each move
    board = pgn.board()
    for move in pgn.mainline_moves():
        board.push(move)
        fens.append(board.fen())

    return fens


def get_structure_sets_from_pgn(pgn_string):
    structures = set()
    fens = extract_fens_from_pgn(pgn_string)
    for fen in fens:
        structures.add(pawns_only_fen(fen))
    return structures


def pawns_only_fen(fen):
    board_layout = fen.split(" ")[0]
    new_layout = []

    for rank in board_layout.split("/"):
        new_rank = ""
        empty_squares = 0

        for char in rank:
            if char in "Pp":
                if empty_squares > 0:
                    new_rank += str(empty_squares)
                    empty_squares = 0
                new_rank += char
            elif char.isdigit():
                empty_squares += int(char)
            else:
                empty_squares += 1

        if empty_squares > 0:
            new_rank += str(empty_squares)

        new_layout.append(new_rank)

    return "/".join(new_layout)


def get_structure_sets_from_lichess(username: str, limit: int) -> List[str]:
    structures = set()
    pgns = lichess.api.user_games(username, max=limit, format=PGN)
    for pgn in pgns:
        structures.update(get_structure_sets_from_pgn(pgn))
    return structures
