import os
import streamlit as st
import pandas as pd
import chess, chess.svg
import base64
import plotly.express as px

st.set_page_config(page_title="Chess Move Explorer", layout="wide")

# LOAD PREFIX DATA

@st.cache_data
def load_prefix_data():
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    csv_path = os.path.join(base_dir, "data", "processed", "prefix_stats.csv")

    df = pd.read_csv(csv_path)
    df["prefix"] = df["prefix"].apply(eval)
    return df

df_prefix = load_prefix_data()

# SESSION STATE

if "board" not in st.session_state:
    st.session_state.board = chess.Board()

if "moves" not in st.session_state:
    st.session_state.moves = []   # list of UCI strings, es ['e2e4', 'e7e5', ...]


# UTILITY: BOARD

def board_svg_html(board):

    """
    Converts the chess board object into an image for browser display, embedding it directly into the HTML code

    3 steps:
    1. chess.svg.board() creates the board image as an SVG text string
    2. the string is converted to bytes (.encode()) and then encoded into Base64 (base64.b64encode) for safe web embedding
    3. the resulting Base64 string is inserted directly into the <img> tag as a Data URI (src="data:image/..."), 
    allowing the browser to render the board instantly
    """
    svg = chess.svg.board(board=board, size=420)
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f'<img src="data:image/svg+xml;base64,{b64}"/>'


# LAYOUT

st.title("♟️ Interactive Chess Move Explorer")
st.write("Enter moves in UCI format (e.g. `e2e4`, `g8f6`) and see win/draw rates for the sequence.")

col_board, col_moves, col_stats = st.columns([1.2, 1, 1])


# LEFT COLUMN: CHESSBOARD

with col_board:
    st.subheader("Board")
    st.write(board_svg_html(st.session_state.board), unsafe_allow_html=True)

    if st.button("♻️ Reset position"):
        st.session_state.board = chess.Board()
        st.session_state.moves = []
        st.rerun()

    if st.button("Undo last move") and st.session_state.moves:
        st.session_state.board.pop()
        st.session_state.moves.pop()
        st.rerun()


# CENTRAL COLUMN: INPUT MOVES

with col_moves:
    st.subheader("Play a move")

    move_input = st.text_input("Move (UCI, es. e2e4)", key="move_input")

    if st.button("Play move"):
        uci = move_input.strip().lower()

        if not uci:
            st.error("Please enter a move.")
        else:
            try:
                move = chess.Move.from_uci(uci)
            except ValueError:
                st.error("Invalid UCI format. Example: e2e4, g8f6.")
            else:
                # Controllo legalità sulla posizione corrente
                if st.session_state.board.is_legal(move):
                    st.session_state.board.push(move)
                    st.session_state.moves.append(uci)
                    st.success(f"Move played: {uci}")
                    st.rerun()  # ricarica la pagina con la nuova posizione
                else:
                    st.error("Illegal move in the current position.")

    st.subheader("Current sequence")
    if st.session_state.moves:
        st.code(" → ".join(st.session_state.moves))
    else:
        st.write("_No moves yet._")



# RIGHT COLUMN: STATS

with col_stats:
    st.subheader("📊 Sequence statistics")

    def lookup(prefix):
        """Find the row in df_prefix corresponding to the exact move sequence."""
        prefix = tuple(prefix)
        row = df_prefix[df_prefix["prefix"] == prefix]
        return row.iloc[0] if len(row) else None

    stats = lookup(st.session_state.moves)

    if stats is None or len(st.session_state.moves) == 0:
        st.info("No statistics available for this sequence yet.")
    else:
        data = {
            'Result': ['White Win', 'Black Win', 'Draw'],
            'Rate': [stats.white_win_rate, stats.black_win_rate, stats.draw_rate]
        }
        df_chart = pd.DataFrame(data)

        # Colors
        colors = {
            'White Win': '#EAEAEA', # Quasi bianco
            'Black Win': '#363636', # Quasi nero
            'Draw': '#A9A9A9'      # Grigio neutro
        }
        
        # Bar chart
        fig = px.bar(
            df_chart, 
            x='Result', 
            y='Rate', 
            title='Win Probability',
            color='Result',
            color_discrete_map=colors,
            height=300,
            # % Y label
            labels={'Rate': 'Probability (%)', 'Result': ''},
        )
        
        # Graph
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("White Win", f"{stats.white_win_rate * 100:.1f}%")
        with col2:
            st.metric("Black Win", f"{stats.black_win_rate * 100:.1f}%")
        with col3:
            st.metric("Draw", f"{stats.draw_rate * 100:.1f}%")

        st.write(f"**Most common opening:** {stats.main_opening}")

        st.divider()
        st.subheader("Next move suggestions")

        prefix = tuple(st.session_state.moves)
        depth = len(prefix)

        df_next = df_prefix[
            df_prefix["prefix"].apply(
                lambda x: len(x) == depth + 1 and x[:depth] == prefix
            )
        ]

        if df_next.empty:
            st.info("No next moves found in the dataset for this sequence.")
        else:
            df_next = df_next.sort_values("count", ascending=False)
            st.dataframe(
                df_next[["prefix", "count", "white_win_rate", "black_win_rate", "draw_rate"]],
                use_container_width=True
            )

