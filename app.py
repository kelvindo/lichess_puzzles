import streamlit as st
from process_puzzles import generate_puzzle_pack_pgn_strings
from generate_puzzles import PuzzleGenerator

INPUT_FILE = "puzzles/middlegame.csv"
PUZZLE_PACKS = ["Opening", "Middlegame", "Endgame", "Mixed"]


@st.cache_resource
def get_puzzle_generator():
    return PuzzleGenerator()


puzzle_generator = get_puzzle_generator()
puzzle_pack = st.selectbox("Puzzle Pack", PUZZLE_PACKS)
num_puzzles = st.slider("Number of Puzzles", 1, 32, 4)

pgn_strings = puzzle_generator.generate_puzzle_pack_pgn_strings(
    puzzle_pack.lower(),
    num_puzzles,
)

st.text_area("PGNs", "".join(pgn_strings), height=1000, key="pgn_text_area")
