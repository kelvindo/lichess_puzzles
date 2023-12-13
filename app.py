import streamlit as st
from generate_puzzles import (
    PuzzleGenerator,
    PUZZLES_OPENINGS_BY_NAME,
    PUZZLES_OPENINGS_BY_USER,
)

import chess

DEFAULT_USERNAME = "trisolaran3"
DEFAULT_OPENING = "French Defense"


@st.cache_resource
def get_puzzle_generator():
    return PuzzleGenerator()


puzzle_generator = get_puzzle_generator()

puzzle_pack = st.selectbox(
    "Puzzle Pack",
    puzzle_generator.get_puzzle_pack_names(),
)
opening_name = ""
if puzzle_pack == PUZZLES_OPENINGS_BY_NAME:
    opening_name = st.selectbox("Opening Name", puzzle_generator.get_opening_names())

username = ""
if puzzle_pack == PUZZLES_OPENINGS_BY_USER:
    username = st.text_input("Lichess Username", DEFAULT_USERNAME)

fen, analysis_url = puzzle_generator.generate_puzzle_fen_string(
    puzzle_pack_name=puzzle_pack,
    target_rating=1400,
    opening_name=opening_name,
    username=username,
)

st.components.v1.iframe(analysis_url, width=370, height=515, scrolling=False)

st.button("Next Puzzle")
