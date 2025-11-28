import os, ast
import chess
import chess.engine
from tqdm import tqdm


def compute_accuracy(moves, engine):

    """ Computes the accuracy of each move in a chess game using Stockfish.
        For every move, the function compares the evaluation before the move and the evaluation
        after the move to measure the loss for the player who moved.

        The loss = |evaluation_before - evaluation_after| is converted into a normalized accuracy score

        Parameters:
        Moves (list of str) = list of UCI strings
        Engine (chess.Engine.SimpleEngine) = Stockfish engine instance

        Returns:
        - accuracies (list) = accuracy score for each move
        - mean_white_accuracy (float) = mean accuracy over all moves played by white
        - mean_black_accuracy (float) = mean accuracy over all moves played by black
        """

    if not isinstance(moves, list):
        raise TypeError("Moves must be a list of UCI strings! ")

    # Convert UCI strings to move object
    try:
        moves = [chess.Move.from_uci(m) for m in moves]
    except Exception:
          raise ValueError("Invalid UCI move found in the list")
          

    board = chess.Board()
    accuracies = []
    
    limit = chess.engine.Limit(time=0.005)

    for move in moves:

                # Identify the player who is about to move
                # board.turn always starts as White and alternates automatically (WHITE -> BLACK -> WHITE ... ) 

                player = board.turn

                # Evaluation before the move
                evaluation_before = engine.analyse(board, limit)["score"].pov(player).wdl().wins

                # Push the move
                board.push(move)

                # Eval after
                evaluation_after = engine.analyse(board, limit)["score"].pov(player).wdl().wins

                # Loss for this move
                loss = abs(evaluation_before - evaluation_after)

                # Accuracy normalized to 0 - 1
                accuracy = 1/(1 + loss)

                accuracies.append(accuracy)


    # Split: White moves = even indices, Black moves = odd indices
    white_accuracy = list(accuracies[0::2])
    black_accuracy = list(accuracies[1::2])

    # Compute mean accuracy
    mean_white_accuracy = round(sum(white_accuracy)/len(white_accuracy),2)
    mean_black_accuracy = round(sum(black_accuracy)/len(black_accuracy),2)

    return accuracies, mean_white_accuracy, mean_black_accuracy


def save_accuracy(df, engine, accuracy_path):
      
    
    df["accuracies"] = None
    df["mean_white_accuracy"] = None
    df["mean_black_accuracy"] = None

    for i in tqdm(range(len(df)), desc="Accuracy"):
            
            moves = df.loc[i, "moves"]

            if isinstance(moves, str):
                  moves = ast.literal_eval(moves)
            
            accuracies, mean_white_accuracy, mean_black_accuracy = compute_accuracy(moves, engine)

            df.loc[i, "accuracies"] = str(accuracies)
            df.loc[i, "mean_white_accuracy"] = mean_white_accuracy
            df.loc[i, "mean_black_accuracy"] = mean_black_accuracy

    # Close the motor here
    engine.quit()
      
    # Save to csv
    df.to_csv(accuracy_path, index = False)

    print(f"Accuracy computed successfully! and saved to {accuracy_path}")

    return df