import pandas as pd

class Ranking:

        def __init__(self, df, min_games = 5, min_moves = 10):
                self.df = df
                self.min_games = min_games
                self.min_moves = min_moves


        def valid_players(self):
                """

                Returns the list of players who played at least 'min_games' games 
                and whose games have at least 'min_moves' moves.

                """

                # Filter out incomplete/short games
                df_valid = self.df[self.df["num_moves"] >= self.min_moves]

                # Count games as White and as Black

                white_counts = df_valid["white"].value_counts()
                black_counts = df_valid["black"].value_counts()

                # Total games played (white + black)
                total_counts = white_counts.add(black_counts, fill_value=0)

                # Keep only players with enough games
                return total_counts[total_counts >= self.min_games].index

        def accuracy_series_by_color(self, color):

                """
                This function returns a series with:
                        index = player's name
                        values = mean accuracy for that color
                """

                # Validate input

                if color.lower() not in ["white", "black"]:
                        raise ValueError("Color must be 'white' or 'black' ")

                acc = f"mean_{color.lower()}_accuracy"

                # Validate columns existance

                if acc not in self.df.columns:
                        raise KeyError(f"Column {acc} not found in dataframe. ")
                
                # Filter players
                allowed = self.valid_players()

                s = self.df.groupby(color)[acc].mean()
                s = s.loc[s.index.isin(allowed)]

                s.index.name = "player"
                s.name = "accuracy"

                return s

        def ranking_color(self, color):
                """
                Ranking of player for a specific color
                """

                s = self.accuracy_series_by_color(color)

                return s.sort_values(ascending=False).reset_index()


        def ranking_overall(self):

                """ Overall ranking combining accuracy as white and black """

                white = self.accuracy_series_by_color("white")
                black = self.accuracy_series_by_color("black")

                combined = pd.concat([white,black])
                final = combined.groupby(combined.index).mean()

                return final.sort_values(ascending=False).reset_index()

        def ranking(self):

                """
                Ask the user which ranking to compute: white, black or overall
                Returns the corresponding ranking Dataframe.
                """

                while True:
                        choice = input("Choose ranking( white /black / overall ): ").lower()

                        if choice in ["white", "black", "overall"]:
                                break

                        print("Invalid choice. Try again. ")

                if choice in ["white", "black"]:
                        return self.ranking_color(choice)
                else:
                        return self.ranking_overall()
                
                
                
                