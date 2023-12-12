import streamlit as st
from generate_puzzles import PuzzleGenerator

import chess

DEFAULT_USERNAME = "trisolaran3"


@st.cache_resource
def get_puzzle_generator():
    return PuzzleGenerator()


puzzle_generator = get_puzzle_generator()

puzzle_pack = st.selectbox(
    "Puzzle Pack",
    puzzle_generator.get_puzzle_pack_names(),
)

username = st.text_input("Lichess Username", DEFAULT_USERNAME)

fen, analysis_url = puzzle_generator.generate_puzzle_fen_string(
    puzzle_pack_name=puzzle_pack,
    target_rating=1400,
    username=username,
)

st.components.v1.iframe(analysis_url, width=370, height=515, scrolling=False)


col1, col2 = st.columns([1, 1])

with col1:
    st.link_button("Analyze", analysis_url)

with col2:
    st.button("Next Puzzle")
