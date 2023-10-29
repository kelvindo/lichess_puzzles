import streamlit as st

from generate_puzzles import PuzzleGenerator


@st.cache_resource
def get_puzzle_generator():
    return PuzzleGenerator()


puzzle_generator = get_puzzle_generator()
puzzle_pack = st.selectbox(
    "Puzzle Pack",
    puzzle_generator.get_puzzle_pack_names(),
)

num_puzzles = st.slider("Number of Puzzles", min_value=1, max_value=32, value=4)

target_elo = st.slider("Target Puzzle ELO", min_value=500, max_value=2000, value=1250)

pgn_strings = puzzle_generator.generate_puzzle_pack_pgn_strings(
    puzzle_pack,
    num_puzzles,
    target_elo,
)

st.text_area("PGNs", "".join(pgn_strings), height=320, key="pgn_text_area")

st.caption(
    "Copy the PGNs above, go to a Lichess study, add chapter, paste the PGNs, and choose 'Orientation: Automatic'"
)
