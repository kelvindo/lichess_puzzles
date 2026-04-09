# 2D Tactics

A chess puzzle training app that presents positions from the [Lichess puzzle database](https://database.lichess.org/#puzzles) on an interactive board. Choose a puzzle pack by game phase (opening, middlegame, endgame, or random), study the position, try moves, and navigate through 50 puzzles per pack.

**Live site:** [kelvindo.github.io/lichess_puzzles](https://kelvindo.github.io/lichess_puzzles/)

## Features

- Interactive chessboard powered by [chessground](https://github.com/lichess-org/chessground) (Lichess's own board UI) with legal move validation via [chess.js](https://github.com/jhlywa/chess.js)
- Board auto-orients based on which side is to move
- Arrow keys to undo/redo moves on the board
- Reset button to restore the original puzzle position
- "Analyze on Lichess" opens the current board state in Lichess analysis
- Progress saved per pack in localStorage
- Puzzle packs organized by game phase: Opening, Middlegame, Endgame, Random
- ELO range 800–1600, 50 puzzles per pack

## File Structure

```
docs/                          # GitHub Pages site (frontend)
├── index.html                 # Landing page with puzzle pack selection
├── script.js                  # Board logic (chessground + chess.js)
├── styles.css                 # Styling
├── pack_template.html         # Template for generating pack pages
├── generate_pack_pages.js     # Node script to generate pack pages from template
├── packs/                     # Generated per-pack pages
│   ├── random.html
│   ├── opening.html
│   ├── middlegame.html
│   └── endgame.html
└── static_puzzles/            # Pre-generated puzzle CSVs served to the frontend
    ├── puzzles_Random_n50_elo800-1600.csv
    ├── puzzles_Opening_n50_elo800-1600.csv
    ├── puzzles_Middlegame_n50_elo800-1600.csv
    └── puzzles_Endgame_n50_elo800-1600.csv

puzzles/                       # Filtered puzzle sets (intermediate data)
├── opening.csv
├── middlegame.csv
├── endgame.csv
├── opening_tag.csv
└── kings_indian.csv

puzzle_packs/                  # PGN puzzle packs (for external use)
├── kings_indian_1.pgn
├── kings_indian_2.pgn
├── middlegame_1.pgn
├── middlegames_2.pgn
├── endgames1.pgn
└── endgames_2.pgn

process_puzzles.py             # Filters the full Lichess DB into themed puzzle sets
generate_puzzles.py            # PuzzleGenerator class for selecting puzzles by rating/theme
generate_static_puzzles.py     # CLI to generate static CSV puzzle packs for the frontend
test_fen_to_image.py           # Quick test script for FEN board rendering
```

## Data Pipeline

The puzzle data flows through three stages:

1. **Source:** Download the full Lichess puzzle database CSV (~3.5M puzzles) from [database.lichess.org](https://database.lichess.org/#puzzles) and place it as `lichess_db_puzzle.csv` in the project root.

2. **Filter:** `process_puzzles.py filter` reads the full database and outputs filtered CSVs to `puzzles/` by theme (opening, middlegame, endgame), applying rating, popularity, and play count thresholds.

3. **Generate:** `generate_static_puzzles.py` reads the filtered CSVs and produces the final puzzle packs in `docs/static_puzzles/` with FEN positions and Lichess analysis URLs.

## Running Locally

**Prerequisites:** Python 3, Node.js

### Serve the site

```bash
cd docs
python3 -m http.server 8080
# Open http://localhost:8080
```

### Regenerate puzzle pack pages (after editing the template)

```bash
cd docs
node generate_pack_pages.js
```

### Regenerate puzzle data (from scratch)

```bash
# 1. Download lichess_db_puzzle.csv from https://database.lichess.org/#puzzles

# 2. Install Python dependencies
pip install python-chess

# 3. Filter the full database into themed sets
python process_puzzles.py filter

# 4. Generate static puzzle CSVs for the frontend
python generate_static_puzzles.py \
  --puzzle_pack Random \
  --num_puzzles 50 \
  --start_elo 800 \
  --end_elo 1600 \
  --output_dir docs/static_puzzles
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `←` | Undo move |
| `→` | Redo move |
| `n` | Next puzzle |
| `p` | Previous puzzle |
