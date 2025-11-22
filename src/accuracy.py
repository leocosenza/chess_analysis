import chess
import chess.engine

def compute_accuracy(moves, engine):

    """ Computes the accuracy of each move in a chess game using Stockfish.
        For every move, the function compares the evaluation before the move and the evaluation
        after the move to measure the loss for the player who moved.

        The loss = |evaluation_before - evaluation_after| is converted into a normalized accuracy score

        Parameters:
        Moves (list) = list of chess.Move objects
        Engine (chess.Engine.SimpleEngine) = Stockfish engine instance

        Returns:
        - accuracies (list) = accuracy score for each move
        - mean_white_accuracy (float) = mean accuracy over all moves played by white
        - mean_black_accuracy (float) = mean accuracy over all moves played by black
        """

    if not isinstance(moves, list):
        raise TypeError("Moves must be a list of chess.move objects! ")

    board = chess.Board()
    accuracies = []
    
    limit = chess.engine.Limit(depth = 8)

    for i, move in enumerate(moves):

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

