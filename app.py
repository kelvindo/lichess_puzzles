import streamlit as st
from generate_puzzles import PuzzleGenerator

import chess


@st.cache_resource
def get_puzzle_generator():
    return PuzzleGenerator()


puzzle_generator = get_puzzle_generator()

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

puzzle_pack = st.selectbox(
    "Puzzle Pack",
    puzzle_generator.get_puzzle_pack_names(),
)

rating_list = [i for i in range(500, 2100, 100)]
# target_rating = st.selectbox(
#     "Target Rating", rating_list, index=int(len(rating_list) / 2)
# )

fen, analysis_url = puzzle_generator.generate_puzzle_fen_string(
    puzzle_pack_name=puzzle_pack,
    target_rating=1400,
)

st.components.v1.iframe(analysis_url, width=370, height=515, scrolling=False)


col1, col2 = st.columns([1, 1])

with col1:
    st.link_button("Analyze", analysis_url)

with col2:
    st.button("Next Puzzle")
