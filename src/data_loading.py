import os
import chess.pgn
import pandas as pd
from tqdm import tqdm

# Build path relative to project

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "Lichess Elite Database")

def load_pgn_games (folder_path):

    """ Load all chess games in PGN format from a folder and return a pandas Dataframe;

        Parameters: 
            folder_path (str) -> path to the folder containing the PGN files

        Returns:
            Pandas.DataFrame with columns: 
            white, black, result, opening, elo, num_moves, moves (list of chess moves)

    """

    if not os.path.exists(folder_path):
         raise FileNotFoundError(f"Folder does not exist {folder_path}")
    
    MAX_FILES = 50
    pgn_files = [f for f in os.listdir(folder_path) if f.endswith("pgn")][:MAX_FILES]
    

    if not pgn_files:
         raise ValueError("No PGN files found in the folder. ")

    games_data = []

    for filename in tqdm(pgn_files, desc="Loading PGN files"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, encoding="utf-8") as pgn:
                while True:
                    game = chess.pgn.read_game(pgn)
                    if game is None:
                        break

                    # extract the key information

                    white = game.headers.get("White")
                    black = game.headers.get("Black")
                    result = game.headers.get("Result")
                    opening = game.headers.get("Opening")
                    eco = game.headers.get("ECO")

                    # Saves moves as UCI strings (better for csv)
                    moves = [m.uci() for m in game.mainline_moves()]

                    # variable for moves count

                    moves_count = len(moves)

                    games_data.append({
                            "white": white,
                            "black": black,
                            "result": result,
                            "opening": opening,
                            "eco": eco,
                            "num_moves": moves_count,
                            "moves": moves
                            })
                    

    return pd.DataFrame(games_data)
    

# This block runs only when the script is executed directly (not when imported)

if __name__ == "__main__":
    print("Loading data..")
    df = load_pgn_games(DATA_PATH)
    print(f"Dataframe created successfully! Loaded {len(df)} games. ")

    # Add preview of the first 3 moves

    df["moves_preview"] = df["moves"].apply(lambda x: x[:3])

    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)

    csv_path = os.path.join(processed_dir, "chess_dataset.csv")
    df.to_csv(csv_path)

    print(f"Dataset saved in {csv_path}")


                        

