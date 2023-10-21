import csv
import chess.pgn
import random
import requests
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

LICHESS_ACCESS_TOKEN = ""
LICHESS_STUDY_ID = ""
LICHESS_IMPORT_STUDY_URL = (
    f"https://lichess.org/api/study/{LICHESS_STUDY_ID}/import-pgn"
)


@dataclass
class PuzzleFilter:
    min_rating: int
    max_rating: int
    min_popularity: int
    min_plays: int
    puzzle_theme_tag: Optional[str]
    puzzle_opening_tag: Optional[str]


PUZZLE_INPUT_FILE = "lichess_db_puzzle.csv"
PUZZLE_FILTER_MAPPING: Dict[str, PuzzleFilter] = {
    "opening": PuzzleFilter(
        min_rating=750,
        max_rating=1500,
        min_popularity=75,
        min_plays=1000,
        puzzle_theme_tag="opening",
        puzzle_opening_tag=None,
    ),
    "middlegame": PuzzleFilter(
        min_rating=750,
        max_rating=1500,
        min_popularity=75,
        min_plays=10000,
        puzzle_theme_tag="middlegame",
        puzzle_opening_tag=None,
    ),
    "endgame": PuzzleFilter(
        min_rating=750,
        max_rating=1500,
        min_popularity=75,
        min_plays=10000,
        puzzle_theme_tag="endgame",
        puzzle_opening_tag=None,
    ),
    "kings_indian": PuzzleFilter(
        min_rating=500,
        max_rating=2000,
        min_popularity=50,
        min_plays=100,
        puzzle_theme_tag="opening",
        puzzle_opening_tag="kings_indian",
    ),
}


def filter_puzzles():
    filtered_puzzles: Dict[str, List[str]] = {}
    with open(PUZZLE_INPUT_FILE, "r") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i % 1000 == 0:
                print(f"Processed {i} rows")
            puzzle = Puzzle.from_dict(row)
            for filter_name, filter in PUZZLE_FILTER_MAPPING.items():
                if puzzle.apply_filter(filter):
                    filtered_puzzles.setdefault(filter_name, []).append(row)

    for filter_name, puzzles in filtered_puzzles.items():
        print(f"{filter_name}: {len(puzzles)}")
        output_file = f"puzzles/{filter_name}.csv"
        with open(output_file, "w") as out:
            writer = csv.DictWriter(out, fieldnames=reader.fieldnames)
            writer.writeheader()
            for row in puzzles:
                writer.writerow(row)


@dataclass
class Puzzle:
    puzzle_id: str
    fen: str
    moves: List[str]
    rating: int
    rating_deviation: int
    popularity: int
    plays: int
    themes: str
    opening_tags: str

    # Example Row
    # {'PuzzleId': '013h1', 'FEN': 'r1bqk1nr/1p3ppp/p3p3/3pP3/1b1PP3/2N5/PP4PP/R1BQKB1R b KQkq - 0 9', 'Moves': 'd5e4 d1a4 c8d7 a4b4', 'Rating': '1206', 'RatingDeviation': '128', 'Popularity': '83', 'NbPlays': '28', 'Themes': 'advantage fork opening short', 'GameUrl': 'https://lichess.org/3L3zhonx/black#18', 'OpeningTags': 'Sicilian_Defense Sicilian_Defense_McDonnell_Attack'}

    def __init__(
        self,
        puzzle_id: str,
        fen: str,
        moves: str,
        rating: str,
        rating_deviation: str,
        popularity: str,
        plays: int,
        themes: str,
        opening_tags: str,
    ):
        self.puzzle_id = puzzle_id
        self.fen = fen
        self.moves = moves.split()
        self.rating = int(rating)
        self.rating_deviation = int(rating_deviation)
        self.popularity = int(popularity)
        self.plays = int(plays)
        self.themes = themes.lower() if themes else ""
        self.opening_tags = opening_tags.lower() if opening_tags else ""

    @classmethod
    def from_dict(cls, d: Dict[str, str]) -> "Puzzle":
        return cls(
            d["PuzzleId"],
            d["FEN"],
            d["Moves"],
            d["Rating"],
            d["RatingDeviation"],
            d["Popularity"],
            d["NbPlays"],
            d["Themes"],
            d["OpeningTags"],
        )

    def apply_filter(self, filter: PuzzleFilter) -> bool:
        return (
            filter.min_rating <= self.rating <= filter.max_rating
            and self.popularity >= filter.min_popularity
            and self.plays >= filter.min_plays
            and (
                filter.puzzle_theme_tag is None
                or filter.puzzle_theme_tag in self.themes
            )
            and (
                filter.puzzle_opening_tag is None
                or filter.puzzle_opening_tag in self.opening_tags
            )
        )

    def generate_puzzle_position(self, defensive: bool) -> Tuple[str, str]:
        game = chess.pgn.Game()
        game.setup(self.fen)

        if defensive:
            return self.fen

        node = game.add_variation(chess.Move.from_uci(self.moves[0]))
        return node.board().fen()


def upload_puzzle(puzzle: Puzzle, fen: str, index: int):
    if "w" in fen:
        orientation = "white"
    else:
        orientation = "black"

    print(
        f'[FEN "{fen}"]\n[SITE "https://lichess.org/training/{puzzle.puzzle_id}"]\n[WHITEELO "{puzzle.rating}"]\n\n*\n'
    )

    # import_params = {
    #     "name": f"Puzzle {index+1}",
    #     "pgn": f'[FEN "{fen}"]\n[SITE "https://lichess.org/training/{puzzle.puzzle_id}"]\n[WHITEELO "{puzzle.rating}"]',
    #     "orientation": orientation,
    #     "variant": "standard",
    # }

    # response = requests.post(
    #     LICHESS_IMPORT_STUDY_URL,
    #     data=import_params,
    #     headers={f"Authorization": f"Bearer {LICHESS_ACCESS_TOKEN}"},
    # )

    # if response.status_code != 200:
    #     print(f"Failed to import PGN. Status code: {response}")


def generate_puzzle_pack_pgn_strings(
    input_file: str, num_puzzles: int = 32
) -> List[str]:
    puzzles = []
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            puzzle = Puzzle.from_dict(row)
            puzzles.append(puzzle)

    pgn_strings = []
    for puzzle in random.sample(puzzles, num_puzzles):
        fen = puzzle.generate_puzzle_position(coin_flip())
        pgn_strings.append(
            f'[FEN "{fen}"]\n[SITE "https://lichess.org/training/{puzzle.puzzle_id}"]\n\n*\n\n'
        )
    return pgn_strings


def generate_puzzle_pack_pgn_file(
    input_file: str, output_file: str, num_puzzles: int = 32
):
    pgn_strings = generate_puzzle_pack_pgn_strings(input_file, num_puzzles)
    with open(output_file, "w") as f:
        for pgn in pgn_strings:
            f.write(pgn)


def coin_flip() -> bool:
    return random.random() > 0.5


def generate_study(input_file: str, num_puzzles: int):
    puzzles: List[Puzzle] = []
    with open(input_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            puzzle = Puzzle.from_dict(row)
            puzzles.append(puzzle)

    random_puzzles = random.sample(puzzles, num_puzzles)

    for i, puzzle in enumerate(random_puzzles):
        fen = puzzle.generate_puzzle_position(coin_flip())
        upload_puzzle(puzzle, fen, i)


def main():
    # filter_puzzles()
    # generate_study("puzzles/endgame.csv", 25)
    generate_puzzle_pack_pgn_file(
        "puzzles/middlegame.csv", "puzzle_packs/middlegames_2.pgn"
    )


if __name__ == "__main__":
    main()
