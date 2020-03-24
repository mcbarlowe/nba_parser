from datetime import datetime
import numpy as np
import pandas as pd


class PbP:
    """
    This class represents one game of of an NBA play by play dataframe. I am
    building methods on top of this class to streamline the calculation of
    stats from the play by player and then insertion into a database of the
    users choosing
    """

    def __init__(self, pbp_df):
        self.df = pbp_df
        self.home_team = pbp_df["home_team_abbrev"].unique()[0]
        self.away_team = pbp_df["away_team_abbrev"].unique()[0]
        self.home_team_id = pbp_df["home_team_id"].unique()[0]
        self.away_team_id = pbp_df["away_team_id"].unique()[0]
        self.game_date = datetime.strptime(pbp_df["game_date"].unique()[0], "%Y-%m-%d")
        self.season = pbp_df["season"].unique()[0]

    def _point_calc_player(self):
        """
        method calculates simple shooting stats like field goals, three points,
        and free throws made and attempted.
        """
        self.df["fgm"] = np.where(
            (self.df["shot_made"] == 1) & (self.df["event_type_de"] == "shot"), 1, 0
        )
        self.df["fga"] = np.where(
            self.df["event_type_de"].str.contains("shot|missed_shot", regex=True), 1, 0
        )
        self.df["tpm"] = np.where(
            (self.df["shot_made"] == 1) & (self.df["is_three"] == 1), 1, 0
        )
        self.df["tpa"] = np.where(self.df["is_three"] == 1, 1, 0)
        self.df["ftm"] = np.where(
            (self.df["shot_made"] == 1)
            & (self.df["event_type_de"].str.contains("free-throw")),
            1,
            0,
        )
        self.df["fta"] = np.where(
            self.df["event_type_de"].str.contains("free-throw"), 1, 0
        )

        player_points_df = (
            self.df.groupby(["player1_id", "game_date", "game_id", "player1_team_id"])[
                ["fgm", "fga", "tpm", "tpa", "ftm", "fta"]
            ]
            .sum()
            .reset_index()
        )
        player_points_df["player1_team_id"] = player_points_df[
            "player1_team_id"
        ].astype(int)
        player_points_df["game_date"] = pd.to_datetime(player_points_df["game_date"])
        player_points_df.rename(
            columns={"player1_id": "player_id", "player1_team_id": "team_id"},
            inplace=True,
        )

        return player_points_df

    def _assist_calc_player(self):
        """
        method to calculat players assist totals from a game play by play
        """
        assists = self.df[
            (self.df["event_type_de"] == "shot") & (self.df["shot_made"] == 1)
        ]

        assists = (
            assists.groupby(["player2_id", "game_id", "game_date", "player2_team_id"])[
                ["eventnum"]
            ]
            .count()
            .reset_index()
        )

        assists["game_date"] = pd.to_datetime(assists["game_date"])
        assists["player2_team_id"] = assists["player2_team_id"].astype(int)
        assists.rename(
            columns={
                "player2_id": "player_id",
                "player2_team_id": "team_id",
                "eventnum": "ast",
            },
            inplace=True,
        )

        return assists

    def __rebound_calc_player(self):
        pass

    def __turnover_calc_player(self):
        pass

    def __foul_calc_player(self):
        pass

    def __steal_calc_player(self):
        pass

    def _block_calc_player(self):
        """
        function to calculate player blocks and return a dataframe with players
        and blocked shots stats along with key columns to join to other dataframes
        """
        blocks = self.df[self.df["event_type_de"] != "jump-ball"]
        blocks = (
            blocks.groupby(["player3_id", "game_id", "game_date", "player3_team_id"])[
                ["is_block"]
            ]
            .sum()
            .reset_index()
        )
        blocks["game_date"] = pd.to_datetime(blocks["game_date"])
        blocks["player3_team_id"] = blocks["player3_team_id"].astype(int)
        blocks.rename(
            columns={
                "player3_id": "player_id",
                "player3_team_id": "team_id",
                "is_block": "blk",
            },
            inplace=True,
        )

        return blocks

    def __plus_minus_player(self):
        pass

    def __point_calc_team(self):
        pass

    def __assist_calc_team(self):
        pass

    def __rebound_calc_team(self):
        pass

    def __turnover_calc_team(self):
        pass

    def __foul_calc_team(self):
        pass

    def __steal_calc_team(self):
        pass

    def __block_calc_team(self):
        pass

    def __plus_minus_team(self):
        pass

    def playerbygamestats(self):
        """
        this function combines all playerbygamestats and returns a dataframe
        containing them
        """
        points = self._point_calc_player()
        blocks = self._block_calc_player()

        playerbygamestats = points.merge(
            blocks, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        playerbygamestats["blk"] = playerbygamestats["blk"].fillna(0).astype(int)

        return playerbygamestats

    def teambygamestats(self):
        pass
