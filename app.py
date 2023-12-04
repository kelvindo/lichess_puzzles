import streamlit as st
from generate_puzzles import PuzzleGenerator

import chess


@st.cache_resource
def get_puzzle_generator():
    return PuzzleGenerator()


puzzle_generator = get_puzzle_generator()

puzzle_pack = st.selectbox(
    "Puzzle Pack",
    puzzle_generator.get_puzzle_pack_names(),
)

rating_list = [i for i in range(500, 2100, 100)]
target_rating = st.selectbox(
    "Target Rating", rating_list, index=int(len(rating_list) / 2)
)

# num_puzzles = st.slider("Number of Puzzles", min_value=1, max_value=32, value=4)

fen, analysis_url = puzzle_generator.generate_puzzle_fen_string(
    puzzle_pack_name=puzzle_pack,
    target_rating=target_rating,
)

# pgn_strings = puzzle_generator.generate_puzzle_pack_pgn_strings(
#     puzzle_pack,
#     num_puzzles,
#     target_rating,
# )


# st.text_area("PGNs", "".join(pgn_strings), height=320, key="pgn_text_area")

# st.caption(
#     "Copy the PGNs above, go to a Lichess study, add chapter, paste the PGNs, and choose 'Orientation: Automatic'"
# )

# flipped = "w" not in fen
# board = chess.Board(fen)
# board_image = chess.svg.board(
#     board,
#     size=600,
#     flipped=flipped,
#     borders=False,
#     colors={
#         "square light": "#f0d9b5",
#         "square dark": "#b58863",
#     },
# )
# st.image(image=board_image)

src = f"https://lichess.org/analysis/fromPosition/{fen}"
st.components.v1.iframe(src, width=800, height=450, scrolling=True)

col1, col2 = st.columns([1, 7])

with col1:
    st.link_button("Analyze", analysis_url)

with col2:
    st.button("Next Puzzle")
