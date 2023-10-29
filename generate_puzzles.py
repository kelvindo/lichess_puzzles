import csv
import random
from process_puzzles import Puzzle
from typing import Dict, List
from dataclasses import dataclass

PUZZLE_FILES = {
    "opening": "puzzles/opening.csv",
    "middlegame": "puzzles/middlegame.csv",
    "endgame": "puzzles/endgame.csv",
}


def coin_flip() -> bool:
    return random.random() > 0.5


class PuzzleGenerator:
    def __init__(self):
        self.puzzle_mapping = self.load_puzzles()

    def load_puzzles(self) -> Dict[str, List[Puzzle]]:
        puzzle_mapping: Dict[str, List[Puzzle]] = {}
        for name, file_name in PUZZLE_FILES.items():
            with open(file_name, "r") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    puzzle = Puzzle.from_dict(row)
                    puzzle_mapping.setdefault(name, []).append(puzzle)
        return puzzle_mapping

    def generate_puzzle_pack_pgn_strings(
        self, puzzle_pack_name, num_puzzles=32
    ) -> List[str]:
        pgn_strings = []
        for puzzle in random.sample(self.puzzle_mapping[puzzle_pack_name], num_puzzles):
            fen = puzzle.generate_puzzle_position(coin_flip())
            pgn_strings.append(
                f'[FEN "{fen}"]\n[SITE "https://lichess.org/training/{puzzle.puzzle_id}"]\n\n*\n\n'
            )
        return pgn_strings
