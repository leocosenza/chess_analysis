import os
import chess.pgn
import pandas as pd

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
    
    pgn_files = [f for f in os.listdir(folder_path) if f.endswith("pgn")]

    if not pgn_files:
         raise ValueError("No PGN files found in the folder. ")

    games_data = []
    max_games = 200
    count = 0

    for filename in pgn_files:
            file_path = os.path.join(folder_path, filename)
            with open(file_path, encoding="utf-8") as pgn:
                while True:
                    game = chess.pgn.read_game(pgn)
                    if game is None or count==max_games:
                        break

                    # extract the key information

                    white = game.headers.get("White")
                    black = game.headers.get("Black")
                    result = game.headers.get("Result")
                    opening = game.headers.get("Opening")
                    eco = game.headers.get("ECO")
                    moves = list(game.mainline_moves())

                    
                    # variable for moves count

                    moves_count = sum(1 for _ in moves)

                    games_data.append({
                            "white": white,
                            "black": black,
                            "result": result,
                            "opening": opening,
                            "eco": eco,
                            "num_moves": moves_count,
                            "moves": moves
                            })
                    
                    count += 1

    return pd.DataFrame(games_data)
    

# This block runs only when the script is executed directly (not when imported)

if __name__ == "__main__":
    print("Loading data..")
    df = load_pgn_games(DATA_PATH)
    print(f"Dataframe created successfully! Loaded {len(df)} games. ")


                        

