import streamlit as st
from process_puzzles import generate_puzzle_pack_pgn_strings

INPUT_FILE = "puzzles/middlegame.csv"

pgn_strings = generate_puzzle_pack_pgn_strings(INPUT_FILE)

st.selectbox("Puzzle Pack", ["Opening", "Middlegame", "Endgame", "Mixed"])

st.text_area("PGNs", "".join(pgn_strings), height=1000, key="pgn_text_area")
