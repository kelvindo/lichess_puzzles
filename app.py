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

rating_list = [i for i in range(500, 2100, 100)]
target_rating = st.selectbox("Target Rating", rating_list, index = int(len(rating_list) / 2))

num_puzzles = st.slider("Number of Puzzles", min_value=1, max_value=32, value=4)


pgn_strings = puzzle_generator.generate_puzzle_pack_pgn_strings(
    puzzle_pack,
    num_puzzles,
    target_rating,
)

st.write(f'Puzzle Pool Size: {len(pgn_strings)}')

st.text_area("PGNs", "".join(pgn_strings), height=320, key="pgn_text_area")

st.caption(
    "Copy the PGNs above, go to a Lichess study, add chapter, paste the PGNs, and choose 'Orientation: Automatic'"
)
