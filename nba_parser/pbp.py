from datetime import datetime
import math
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
        self.season = pbp_df["season"].unique()[0]

        # done to handle PbP classes created from imported csv files versus
        # those that are created by nba_scraper that handles game_date as a
        # proper datetime dtype
        if self.df["game_date"].dtypes == "O":
            self.game_date = datetime.strptime(
                pbp_df["game_date"].unique()[0], "%Y-%m-%d"
            )
            self.df["game_date"] = pd.to_datetime(self.df["game_date"])
        else:
            self.game_date = pbp_df["game_date"].unique()[0]

        # change column types to fit my database at a later time on insert

        self.df["scoremargin"] = self.df["scoremargin"].astype(str)

        # calculating home and away possesions to later aggregate for players
        # and teams

        # calculating made shot possessions
        self.df["home_possession"] = np.where(
            (self.df.event_team == self.df.home_team_abbrev)
            & (self.df.event_type_de == "shot"),
            1,
            0,
        )
        # calculating turnover possessions
        self.df["home_possession"] = np.where(
            (self.df.event_team == self.df.home_team_abbrev)
            & (self.df.event_type_de == "turnover"),
            1,
            self.df["home_possession"],
        )
        # calculating defensive rebound possessions
        self.df["home_possession"] = np.where(
            (
                (self.df.event_team == self.df.away_team_abbrev)
                & (self.df.is_d_rebound == 1)
            )
            | (
                (self.df.event_type_de == "rebound")
                & (self.df.is_d_rebound == 0)
                & (self.df.is_o_rebound == 0)
                & (self.df.event_team == self.df.away_team_abbrev)
                & (self.df.event_type_de.shift(1) != "free-throw")
            ),
            1,
            self.df["home_possession"],
        )
        # calculating final free throw possessions
        self.df["home_possession"] = np.where(
            (self.df.event_team == self.df.home_team_abbrev)
            & (
                (self.df.homedescription.str.contains("Free Throw 2 of 2"))
                | (self.df.homedescription.str.contains("Free Throw 3 of 3"))
            ),
            1,
            self.df["home_possession"],
        )
        # calculating made shot possessions
        self.df["away_possession"] = np.where(
            (self.df.event_team == self.df.away_team_abbrev)
            & (self.df.event_type_de == "shot"),
            1,
            0,
        )
        # calculating turnover possessions
        self.df["away_possession"] = np.where(
            (self.df.event_team == self.df.away_team_abbrev)
            & (self.df.event_type_de == "turnover"),
            1,
            self.df["away_possession"],
        )
        # calculating defensive rebound possessions
        self.df["away_possession"] = np.where(
            (
                (self.df.event_team == self.df.home_team_abbrev)
                & (self.df.is_d_rebound == 1)
            )
            | (
                (self.df.event_type_de == "rebound")
                & (self.df.is_d_rebound == 0)
                & (self.df.is_o_rebound == 0)
                & (self.df.event_team == self.df.home_team_abbrev)
                & (self.df.event_type_de.shift(1) != "free-throw")
            ),
            1,
            self.df["away_possession"],
        )
        # calculating final free throw possessions
        self.df["away_possession"] = np.where(
            (self.df.event_team == self.df.away_team_abbrev)
            & (
                (self.df.visitordescription.str.contains("Free Throw 2 of 2"))
                | (self.df.visitordescription.str.contains("Free Throw 3 of 3"))
            ),
            1,
            self.df["away_possession"],
        )

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
                ["fgm", "fga", "tpm", "tpa", "ftm", "fta", "points_made"]
            ]
            .sum()
            .reset_index()
        )
        player_points_df["player1_team_id"] = player_points_df[
            "player1_team_id"
        ].astype(int)
        player_points_df.rename(
            columns={
                "player1_id": "player_id",
                "player1_team_id": "team_id",
                "points_made": "points",
            },
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

    def _rebound_calc_player(self):
        """
        function to calculate player's offensive and defensive rebound totals
        """
        rebounds = (
            self.df.groupby(["player1_id", "game_id", "game_date"])[
                ["is_o_rebound", "is_d_rebound"]
            ]
            .sum()
            .reset_index()
        )

        rebounds.rename(
            columns={
                "player1_id": "player_id",
                "is_o_rebound": "oreb",
                "is_d_rebound": "dreb",
            },
            inplace=True,
        )

        return rebounds

    def _turnover_calc_player(self):
        """
        function to calculate player's turnover totals
        """
        turnovers = (
            self.df.groupby(["player1_id", "game_id", "game_date", "player1_team_id"])[
                ["is_turnover"]
            ]
            .sum()
            .reset_index()
        )

        turnovers["player1_team_id"] = turnovers["player1_team_id"].astype(int)
        turnovers.rename(
            columns={
                "player1_id": "player_id",
                "player1_team_id": "team_id",
                "is_turnover": "tov",
            },
            inplace=True,
        )

        return turnovers

    def _foul_calc_player(self):
        """
        method to calculate players personal fouls in a game
        """
        fouls = self.df[
            (self.df["event_type_de"] == "foul")
            & (
                self.df["eventmsgactiontype"].isin(
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 26, 27, 28]
                )
            )
        ]
        fouls = (
            fouls.groupby(["player1_id", "game_id", "game_date", "player1_team_id"])[
                "eventnum"
            ]
            .count()
            .reset_index()
        )
        fouls["player1_team_id"] = fouls["player1_team_id"].astype(int)
        fouls.rename(
            columns={
                "player1_id": "player_id",
                "player1_team_id": "team_id",
                "eventnum": "pf",
            },
            inplace=True,
        )

        return fouls

    def _steal_calc_player(self):
        """
        function to calculate player's steal totals
        """
        steals = (
            self.df.groupby(["player2_id", "game_id", "game_date", "player2_team_id"])[
                ["is_steal"]
            ]
            .sum()
            .reset_index()
        )

        steals["player2_team_id"] = steals["player2_team_id"].astype(int)
        steals.rename(
            columns={
                "player2_id": "player_id",
                "player2_team_id": "team_id",
                "is_steal": "stl",
            },
            inplace=True,
        )
        return steals

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

    def _plus_minus_calc_player(self):

        self.df["home_plus"] = np.where(
            self.df["event_team"] == self.df["home_team_abbrev"],
            self.df["points_made"],
            0,
        )
        self.df["home_minus"] = np.where(
            self.df["event_team"] != self.df["home_team_abbrev"],
            self.df["points_made"],
            0,
        )
        self.df["away_plus"] = np.where(
            self.df["event_team"] != self.df["home_team_abbrev"],
            self.df["points_made"],
            0,
        )
        self.df["away_minus"] = np.where(
            self.df["event_team"] == self.df["home_team_abbrev"],
            self.df["points_made"],
            0,
        )

        no_ft_df = self.df[self.df["event_type_de"] != "free-throw"].copy()

        home_player_1 = (
            no_ft_df.groupby(
                ["home_player_1_id", "game_id", "game_date", "home_team_id"]
            )[["home_plus", "home_minus"]]
            .sum()
            .reset_index()
        )
        home_player_1.rename(
            columns={
                "home_player_1_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )
        home_player_2 = (
            no_ft_df.groupby(
                ["home_player_2_id", "game_id", "game_date", "home_team_id"]
            )[["home_plus", "home_minus"]]
            .sum()
            .reset_index()
        )
        home_player_2.rename(
            columns={
                "home_player_2_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )
        home_player_3 = (
            no_ft_df.groupby(
                ["home_player_3_id", "game_id", "game_date", "home_team_id"]
            )[["home_plus", "home_minus"]]
            .sum()
            .reset_index()
        )
        home_player_3.rename(
            columns={
                "home_player_3_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )
        home_player_4 = (
            no_ft_df.groupby(
                ["home_player_4_id", "game_id", "game_date", "home_team_id"]
            )[["home_plus", "home_minus"]]
            .sum()
            .reset_index()
        )
        home_player_4.rename(
            columns={
                "home_player_4_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )
        home_player_5 = (
            no_ft_df.groupby(
                ["home_player_5_id", "game_id", "game_date", "home_team_id"]
            )[["home_plus", "home_minus"]]
            .sum()
            .reset_index()
        )
        home_player_5.rename(
            columns={
                "home_player_5_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )

        away_player_1 = (
            no_ft_df.groupby(
                ["away_player_1_id", "game_id", "game_date", "away_team_id"]
            )[["away_plus", "away_minus"]]
            .sum()
            .reset_index()
        )
        away_player_1.rename(
            columns={
                "away_player_1_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_2 = (
            no_ft_df.groupby(
                ["away_player_2_id", "game_id", "game_date", "away_team_id"]
            )[["away_plus", "away_minus"]]
            .sum()
            .reset_index()
        )
        away_player_2.rename(
            columns={
                "away_player_2_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_3 = (
            no_ft_df.groupby(
                ["away_player_3_id", "game_id", "game_date", "away_team_id"]
            )[["away_plus", "away_minus"]]
            .sum()
            .reset_index()
        )
        away_player_3.rename(
            columns={
                "away_player_3_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_4 = (
            no_ft_df.groupby(
                ["away_player_4_id", "game_id", "game_date", "away_team_id"]
            )[["away_plus", "away_minus"]]
            .sum()
            .reset_index()
        )
        away_player_4.rename(
            columns={
                "away_player_4_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_5 = (
            no_ft_df.groupby(
                ["away_player_5_id", "game_id", "game_date", "away_team_id"]
            )[["away_plus", "away_minus"]]
            .sum()
            .reset_index()
        )
        away_player_5.rename(
            columns={
                "away_player_5_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )

        home_plus_minus_total = pd.concat(
            [home_player_1, home_player_2, home_player_3, home_player_4, home_player_5,]
        )
        away_plus_minus_total = pd.concat(
            [away_player_1, away_player_2, away_player_3, away_player_4, away_player_5,]
        )

        home_plus_minus = (
            home_plus_minus_total.groupby(
                ["player_id", "game_id", "game_date", "team_id"]
            )[["plus", "minus"]]
            .sum()
            .reset_index()
        )

        away_plus_minus = (
            away_plus_minus_total.groupby(
                ["player_id", "game_id", "game_date", "team_id"]
            )[["plus", "minus"]]
            .sum()
            .reset_index()
        )

        plus_minus = pd.concat([home_plus_minus, away_plus_minus])

        # calculating plus minus for free throw events
        foul_df = self.df[self.df["event_type_de"] == "foul"][
            [
                "period",
                "seconds_elapsed",
                "pctimestring",
                "home_player_1_id",
                "home_player_2_id",
                "home_player_3_id",
                "home_player_4_id",
                "home_player_5_id",
                "away_player_1_id",
                "away_player_2_id",
                "away_player_3_id",
                "away_player_4_id",
                "away_player_5_id",
            ]
        ].copy()

        ft_df = self.df[self.df["event_type_de"] == "free-throw"][
            [
                "period",
                "seconds_elapsed",
                "pctimestring",
                "game_id",
                "game_date",
                "home_team_id",
                "away_team_id",
                "home_plus",
                "home_minus",
                "away_plus",
                "away_minus",
            ]
        ]

        ft_df = ft_df.merge(foul_df, on=["period", "seconds_elapsed", "pctimestring"])

        home_player_1 = (
            ft_df.groupby(["home_player_1_id", "game_id", "game_date", "home_team_id"])[
                ["home_plus", "home_minus"]
            ]
            .sum()
            .reset_index()
        )

        home_player_1.rename(
            columns={
                "home_player_1_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )

        home_player_2 = (
            ft_df.groupby(["home_player_2_id", "game_id", "game_date", "home_team_id"])[
                ["home_plus", "home_minus"]
            ]
            .sum()
            .reset_index()
        )

        home_player_2.rename(
            columns={
                "home_player_2_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )
        home_player_3 = (
            ft_df.groupby(["home_player_3_id", "game_id", "game_date", "home_team_id"])[
                ["home_plus", "home_minus"]
            ]
            .sum()
            .reset_index()
        )
        home_player_3.rename(
            columns={
                "home_player_3_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )
        home_player_4 = (
            ft_df.groupby(["home_player_4_id", "game_id", "game_date", "home_team_id"])[
                ["home_plus", "home_minus"]
            ]
            .sum()
            .reset_index()
        )
        home_player_4.rename(
            columns={
                "home_player_4_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )
        home_player_5 = (
            ft_df.groupby(["home_player_5_id", "game_id", "game_date", "home_team_id"])[
                ["home_plus", "home_minus"]
            ]
            .sum()
            .reset_index()
        )
        home_player_5.rename(
            columns={
                "home_player_5_id": "player_id",
                "home_team_id": "team_id",
                "home_plus": "plus",
                "home_minus": "minus",
            },
            inplace=True,
        )

        away_player_1 = (
            ft_df.groupby(["away_player_1_id", "game_id", "game_date", "away_team_id"])[
                ["away_plus", "away_minus"]
            ]
            .sum()
            .reset_index()
        )
        away_player_1.rename(
            columns={
                "away_player_1_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_2 = (
            ft_df.groupby(["away_player_2_id", "game_id", "game_date", "away_team_id"])[
                ["away_plus", "away_minus"]
            ]
            .sum()
            .reset_index()
        )
        away_player_2.rename(
            columns={
                "away_player_2_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_3 = (
            ft_df.groupby(["away_player_3_id", "game_id", "game_date", "away_team_id"])[
                ["away_plus", "away_minus"]
            ]
            .sum()
            .reset_index()
        )
        away_player_3.rename(
            columns={
                "away_player_3_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_4 = (
            ft_df.groupby(["away_player_4_id", "game_id", "game_date", "away_team_id"])[
                ["away_plus", "away_minus"]
            ]
            .sum()
            .reset_index()
        )
        away_player_4.rename(
            columns={
                "away_player_4_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )
        away_player_5 = (
            ft_df.groupby(["away_player_5_id", "game_id", "game_date", "away_team_id"])[
                ["away_plus", "away_minus"]
            ]
            .sum()
            .reset_index()
        )
        away_player_5.rename(
            columns={
                "away_player_5_id": "player_id",
                "away_team_id": "team_id",
                "away_plus": "plus",
                "away_minus": "minus",
            },
            inplace=True,
        )

        home_ft_plus_minus_total = pd.concat(
            [home_player_1, home_player_2, home_player_3, home_player_4, home_player_5,]
        )
        away_ft_plus_minus_total = pd.concat(
            [away_player_1, away_player_2, away_player_3, away_player_4, away_player_5,]
        )

        home_plus_minus_ft = (
            home_ft_plus_minus_total.groupby(
                ["player_id", "game_id", "game_date", "team_id"]
            )[["plus", "minus"]]
            .sum()
            .reset_index()
        )

        away_plus_minus_ft = (
            away_ft_plus_minus_total.groupby(
                ["player_id", "game_id", "game_date", "team_id"]
            )[["plus", "minus"]]
            .sum()
            .reset_index()
        )

        ft_plus_minus = pd.concat([home_plus_minus_ft, away_plus_minus_ft])

        # combining free-throw and non free-throw plus minus dataframes into one
        total_plus_minus = pd.concat([ft_plus_minus, plus_minus])
        total_plus_minus = (
            total_plus_minus.groupby(["player_id", "game_id", "game_date", "team_id"])[
                ["plus", "minus"]
            ]
            .sum()
            .reset_index()
        )
        total_plus_minus["plus_minus"] = (
            total_plus_minus["plus"] - total_plus_minus["minus"]
        )

        return total_plus_minus

    def _toc_calc_player(self):
        """
        this method calculates a players time in the game and converts it to
        a time string of MM:SS as well
        """

        # home players time on court (toc) calculations
        home_player_1 = (
            self.df.groupby(
                ["home_player_1_id", "game_id", "game_date", "home_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        home_player_1.rename(
            columns={
                "home_player_1_id": "player_id",
                "home_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        home_player_2 = (
            self.df.groupby(
                ["home_player_2_id", "game_id", "game_date", "home_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        home_player_2.rename(
            columns={
                "home_player_2_id": "player_id",
                "home_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        home_player_3 = (
            self.df.groupby(
                ["home_player_3_id", "game_id", "game_date", "home_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        home_player_3.rename(
            columns={
                "home_player_3_id": "player_id",
                "home_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        home_player_4 = (
            self.df.groupby(
                ["home_player_4_id", "game_id", "game_date", "home_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        home_player_4.rename(
            columns={
                "home_player_4_id": "player_id",
                "home_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        home_player_5 = (
            self.df.groupby(
                ["home_player_5_id", "game_id", "game_date", "home_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        home_player_5.rename(
            columns={
                "home_player_5_id": "player_id",
                "home_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )

        home_players_toc = pd.concat(
            [home_player_1, home_player_2, home_player_3, home_player_4, home_player_5]
        )
        home_players_toc = (
            home_players_toc.groupby(["player_id", "team_id", "game_id", "game_date"])[
                ["toc"]
            ]
            .sum()
            .reset_index()
        )

        home_players_toc["toc_string"] = pd.to_datetime(
            home_players_toc["toc"], unit="s"
        ).dt.strftime("%M:%S")

        # away players time on court (toc) calculations
        away_player_1 = (
            self.df.groupby(
                ["away_player_1_id", "game_id", "game_date", "away_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )

        away_player_1.rename(
            columns={
                "away_player_1_id": "player_id",
                "away_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        away_player_2 = (
            self.df.groupby(
                ["away_player_2_id", "game_id", "game_date", "away_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        away_player_2.rename(
            columns={
                "away_player_2_id": "player_id",
                "away_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        away_player_3 = (
            self.df.groupby(
                ["away_player_3_id", "game_id", "game_date", "away_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        away_player_3.rename(
            columns={
                "away_player_3_id": "player_id",
                "away_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        away_player_4 = (
            self.df.groupby(
                ["away_player_4_id", "game_id", "game_date", "away_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        away_player_4.rename(
            columns={
                "away_player_4_id": "player_id",
                "away_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )
        away_player_5 = (
            self.df.groupby(
                ["away_player_5_id", "game_id", "game_date", "away_team_id"]
            )[["event_length"]]
            .sum()
            .reset_index()
        )
        away_player_5.rename(
            columns={
                "away_player_5_id": "player_id",
                "away_team_id": "team_id",
                "event_length": "toc",
            },
            inplace=True,
        )

        away_players_toc = pd.concat(
            [away_player_1, away_player_2, away_player_3, away_player_4, away_player_5]
        )
        away_players_toc = (
            away_players_toc.groupby(["player_id", "team_id", "game_id", "game_date"])[
                ["toc"]
            ]
            .sum()
            .reset_index()
        )

        away_players_toc["toc_string"] = pd.to_datetime(
            away_players_toc["toc"], unit="s"
        ).dt.strftime("%M:%S")

        total_toc = pd.concat([home_players_toc, away_players_toc])

        return total_toc

    def _poss_calc_player(self):
        """
        function to calculate possessions each player participated in
        """

        # calculating player possesions
        player1 = self.df[
            [
                "home_player_1",
                "home_player_1_id",
                "home_possession",
                "game_id",
                "home_team_id",
            ]
        ].rename(
            columns={"home_player_1": "player_name", "home_player_1_id": "player_id"}
        )
        player2 = self.df[
            [
                "home_player_2",
                "home_player_2_id",
                "home_possession",
                "game_id",
                "home_team_id",
            ]
        ].rename(
            columns={"home_player_2": "player_name", "home_player_2_id": "player_id"}
        )
        player3 = self.df[
            [
                "home_player_3",
                "home_player_3_id",
                "home_possession",
                "game_id",
                "home_team_id",
            ]
        ].rename(
            columns={"home_player_3": "player_name", "home_player_3_id": "player_id"}
        )
        player4 = self.df[
            [
                "home_player_4",
                "home_player_4_id",
                "home_possession",
                "game_id",
                "home_team_id",
            ]
        ].rename(
            columns={"home_player_4": "player_name", "home_player_4_id": "player_id"}
        )
        player5 = self.df[
            [
                "home_player_5",
                "home_player_5_id",
                "home_possession",
                "game_id",
                "home_team_id",
            ]
        ].rename(
            columns={"home_player_5": "player_name", "home_player_5_id": "player_id"}
        )
        home_possession_df = pd.concat([player1, player2, player3, player4, player5])
        home_possession_df = (
            home_possession_df.groupby(
                ["player_id", "player_name", "game_id", "home_team_id"]
            )["home_possession"]
            .sum()
            .reset_index()
            .sort_values("home_possession")
        )
        player1 = self.df[
            [
                "away_player_1",
                "away_player_1_id",
                "away_possession",
                "game_id",
                "away_team_id",
            ]
        ].rename(
            columns={"away_player_1": "player_name", "away_player_1_id": "player_id"}
        )
        player2 = self.df[
            [
                "away_player_2",
                "away_player_2_id",
                "away_possession",
                "game_id",
                "away_team_id",
            ]
        ].rename(
            columns={"away_player_2": "player_name", "away_player_2_id": "player_id"}
        )
        player3 = self.df[
            [
                "away_player_3",
                "away_player_3_id",
                "away_possession",
                "game_id",
                "away_team_id",
            ]
        ].rename(
            columns={"away_player_3": "player_name", "away_player_3_id": "player_id"}
        )
        player4 = self.df[
            [
                "away_player_4",
                "away_player_4_id",
                "away_possession",
                "game_id",
                "away_team_id",
            ]
        ].rename(
            columns={"away_player_4": "player_name", "away_player_4_id": "player_id"}
        )
        player5 = self.df[
            [
                "away_player_5",
                "away_player_5_id",
                "away_possession",
                "game_id",
                "away_team_id",
            ]
        ].rename(
            columns={"away_player_5": "player_name", "away_player_5_id": "player_id"}
        )
        away_possession_df = pd.concat([player1, player2, player3, player4, player5])
        away_possession_df = (
            away_possession_df.groupby(
                ["player_id", "player_name", "game_id", "away_team_id"]
            )["away_possession"]
            .sum()
            .reset_index()
            .sort_values("away_possession")
        )

        home_possession_df = home_possession_df.rename(
            columns={"home_team_id": "team_id", "home_possession": "possessions"}
        )
        away_possession_df = away_possession_df.rename(
            columns={"away_team_id": "team_id", "away_possession": "possessions"}
        )
        possession_df = pd.concat([home_possession_df, away_possession_df])

        return possession_df

    def _poss_calc_team(self):
        """
        method to calculate team possession numbers
        """

        row1 = [
            self.df.home_team_id.unique()[0],
            self.df.game_id.unique()[0],
            self.df.home_team_abbrev.unique()[0],
            self.df["home_possession"].sum(),
        ]
        row2 = [
            self.df.away_team_id.unique()[0],
            self.df.game_id.unique()[0],
            self.df.away_team_abbrev.unique()[0],
            self.df["away_possession"].sum(),
        ]
        team_possession_df = pd.DataFrame(
            [row1, row2], columns=["team_id", "game_id", "team_abbrev", "possessions"]
        )

        return team_possession_df

    def _point_calc_team(self):
        """
        method to calculate team field goals, free throws, and three points
        made
        """
        self.df["fg_attempted"] = np.where(
            self.df["event_type_de"].isin(["missed_shot", "shot"]), True, False
        )
        self.df["ft_attempted"] = np.where(
            self.df["event_type_de"] == "free-throw", True, False
        )
        self.df["fg_made"] = np.where(
            (self.df["event_type_de"].isin(["shot"])) & (self.df["points_made"] > 0),
            True,
            False,
        )
        self.df["tp_made"] = np.where(self.df["points_made"] == 3, True, False)
        self.df["ft_made"] = np.where(
            (self.df["event_type_de"] == "free-throw") & (self.df["points_made"] == 1),
            True,
            False,
        )
        teams_df = (
            self.df.groupby(["player1_team_id", "game_id"])[
                [
                    "points_made",
                    "is_three",
                    "fg_attempted",
                    "ft_attempted",
                    "fg_made",
                    "tp_made",
                    "ft_made",
                ]
            ]
            .sum()
            .reset_index()
        )
        teams_df["player1_team_id"] = teams_df["player1_team_id"].astype(int)
        teams_df.rename(
            columns={
                "player1_team_id": "team_id",
                "points_made": "points_for",
                "is_three": "tpa",
                "fg_made": "fgm",
                "fg_attempted": "fga",
                "ft_made": "ftm",
                "ft_attempted": "fta",
                "tp_made": "tpm",
            },
            inplace=True,
        )

        return teams_df

    def _assist_calc_team(self):
        """
        method to sum assists made for each team
        """
        self.df["is_assist"] = np.where(
            (self.df["event_type_de"] == "shot") & (self.df["player2_id"] != 0),
            True,
            False,
        )
        assists_df = (
            self.df.groupby(["player1_team_id", "game_id"])[["is_assist"]]
            .sum()
            .reset_index()
        )
        assists_df.rename(
            columns={"is_assist": "ast", "player1_team_id": "team_id",}, inplace=True,
        )

        return assists_df

    def _rebound_calc_team(self):
        """
        method to calculate team offensive and deffensive rebound totals
        """
        rebounds_df = (
            self.df.groupby(["player1_team_id", "game_id"])[
                ["is_d_rebound", "is_o_rebound",]
            ]
            .sum()
            .reset_index()
        )
        rebounds_df["player1_team_id"] = rebounds_df["player1_team_id"].astype(int)
        rebounds_df.rename(
            columns={
                "player1_team_id": "team_id",
                "is_d_rebound": "dreb",
                "is_o_rebound": "oreb",
            },
            inplace=True,
        )

        return rebounds_df

    def _turnover_calc_team(self):
        turnovers_df = (
            self.df.groupby(["player1_team_id", "game_id"])[["is_turnover"]]
            .sum()
            .reset_index()
        )
        turnovers_df["player1_team_id"] = turnovers_df["player1_team_id"].astype(int)
        turnovers_df.rename(
            columns={"player1_team_id": "team_id", "is_turnover": "tov",}, inplace=True,
        )

        return turnovers_df

    def _foul_calc_team(self):
        """
        method to calculate team personal fouls taken in a game
        """

        fouls = self.df[
            (self.df["event_type_de"] == "foul")
            & (
                self.df["eventmsgactiontype"].isin(
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 14, 15, 26, 27, 28]
                )
            )
        ]
        fouls = (
            fouls.groupby(["game_id", "player1_team_id"])["eventnum"]
            .count()
            .reset_index()
        )
        fouls["player1_team_id"] = fouls["player1_team_id"].astype(int)
        fouls.rename(
            columns={"player1_team_id": "team_id", "eventnum": "pf",}, inplace=True,
        )

        fouls = fouls.merge(fouls, on="game_id", suffixes=["", "_opponent"])

        fouls = fouls[fouls["team_id"] != fouls["team_id_opponent"]]
        fouls.rename(
            columns={"pf_opponent": "fouls_drawn",}, inplace=True,
        )

        return fouls[["team_id", "game_id", "pf", "fouls_drawn"]]

    def _steal_calc_team(self):
        """
        method to calculate team steals in a game
        """

        steals_df = (
            self.df.groupby(["player2_team_id", "game_id"])[["is_steal"]]
            .sum()
            .reset_index()
        )
        steals_df["player2_team_id"] = steals_df["player2_team_id"].astype(int)
        steals_df.rename(
            columns={"player2_team_id": "team_id", "is_steal": "stl",}, inplace=True,
        )

        return steals_df

    def _block_calc_team(self):
        """
        method to calculate team blocks
        """
        blocks_df = (
            self.df.groupby(["player3_team_id", "game_id"])[["is_block"]]
            .sum()
            .reset_index()
        )
        blocks_df["player3_team_id"] = blocks_df["player3_team_id"].astype(int)
        blocks_df.rename(
            columns={"player3_team_id": "team_id", "is_block": "blk",}, inplace=True,
        )

        blocks_df = blocks_df.merge(blocks_df, on="game_id", suffixes=["", "_opponent"])

        blocks_df = blocks_df[blocks_df["team_id"] != blocks_df["team_id_opponent"]]
        blocks_df.rename(
            columns={"blk_opponent": "shots_blocked",}, inplace=True,
        )

        return blocks_df[["team_id", "game_id", "blk", "shots_blocked"]]

    def _plus_minus_team(self):
        """
        method to calculate team score differential
        """
        plus_minus_df = (
            self.df.groupby(["player1_team_id", "game_id"])[["points_made",]]
            .sum()
            .reset_index()
        )
        plus_minus_df["player1_team_id"] = plus_minus_df["player1_team_id"].astype(int)
        plus_minus_df.rename(
            columns={"player1_team_id": "team_id", "points_made": "points_for",},
            inplace=True,
        )
        plus_minus_df = plus_minus_df.merge(
            plus_minus_df, on="game_id", suffixes=["", "_opponent"]
        )

        plus_minus_df = plus_minus_df[
            plus_minus_df["team_id"] != plus_minus_df["team_id_opponent"]
        ]

        plus_minus_df["plus_minus"] = (
            plus_minus_df["points_for"] - plus_minus_df["points_for_opponent"]
        )
        plus_minus_df.rename(
            columns={"points_for_opponent": "points_against",}, inplace=True,
        )

        return plus_minus_df[["team_id", "game_id", "points_against", "plus_minus"]]

    @staticmethod
    def parse_possessions(poss_list):
        """
        a function to parse each possession and create one row for offense team
        and defense team

        Inputs:
        poss_list   - list of dataframes each one representing one possession

        Outputs:
        parsed_list  - list of dataframes where each list inside represents the players on
                       off and def and points score for each possession
        """
        parsed_list = []

        for df in poss_list:
            if df.loc[df.index[-1], "event_type_de"] in ["rebound", "turnover"]:
                if df.loc[df.index[-1], "event_type_de"] == "turnover":
                    if (
                        df.loc[df.index[-1], "event_team"]
                        == df.loc[df.index[-1], "home_team_abbrev"]
                    ):
                        row_df = pd.concat(
                            [
                                df.loc[
                                    df.index[-1], "home_player_1":"away_player_5_id"
                                ],
                                df.loc[
                                    df.index[-1],
                                    [
                                        "points_made_y",
                                        "home_team_abbrev",
                                        "event_team",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                ],
                            ]
                        )

                        parsed_list.extend(
                            [
                                pd.DataFrame(
                                    [list(row_df)],
                                    columns=[
                                        "off_player_1",
                                        "off_player_1_id",
                                        "off_player_2",
                                        "off_player_2_id",
                                        "off_player_3",
                                        "off_player_3_id",
                                        "off_player_4",
                                        "off_player_4_id",
                                        "off_player_5",
                                        "off_player_5_id",
                                        "def_player_1",
                                        "def_player_1_id",
                                        "def_player_2",
                                        "def_player_2_id",
                                        "def_player_3",
                                        "def_player_3_id",
                                        "def_player_4",
                                        "def_player_4_id",
                                        "def_player_5",
                                        "def_player_5_id",
                                        "points_made",
                                        "home_team_abbrev",
                                        "event_team_abbrev",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                )
                            ]
                        )
                    elif (
                        df.loc[df.index[-1], "event_team"]
                        == df.loc[df.index[-1], "away_team_abbrev"]
                    ):
                        row_df = pd.concat(
                            [
                                df.loc[
                                    df.index[-1], "home_player_1":"away_player_5_id"
                                ],
                                df.loc[
                                    df.index[-1],
                                    [
                                        "points_made_y",
                                        "home_team_abbrev",
                                        "event_team",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                ],
                            ]
                        )

                        parsed_list.extend(
                            [
                                pd.DataFrame(
                                    [list(row_df)],
                                    columns=[
                                        "def_player_1",
                                        "def_player_1_id",
                                        "def_player_2",
                                        "def_player_2_id",
                                        "def_player_3",
                                        "def_player_3_id",
                                        "def_player_4",
                                        "def_player_4_id",
                                        "def_player_5",
                                        "def_player_5_id",
                                        "off_player_1",
                                        "off_player_1_id",
                                        "off_player_2",
                                        "off_player_2_id",
                                        "off_player_3",
                                        "off_player_3_id",
                                        "off_player_4",
                                        "off_player_4_id",
                                        "off_player_5",
                                        "off_player_5_id",
                                        "points_made",
                                        "home_team_abbrev",
                                        "event_team_abbrev",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                )
                            ]
                        )
                if df.loc[df.index[-1], "event_type_de"] == "rebound":
                    if (
                        df.loc[df.index[-1], "event_team"]
                        == df.loc[df.index[-1], "away_team_abbrev"]
                    ):
                        row_df = pd.concat(
                            [
                                df.loc[
                                    df.index[-1], "home_player_1":"away_player_5_id"
                                ],
                                df.loc[
                                    df.index[-1],
                                    [
                                        "points_made_y",
                                        "home_team_abbrev",
                                        "event_team",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                ],
                            ]
                        )

                        parsed_list.extend(
                            [
                                pd.DataFrame(
                                    [list(row_df)],
                                    columns=[
                                        "off_player_1",
                                        "off_player_1_id",
                                        "off_player_2",
                                        "off_player_2_id",
                                        "off_player_3",
                                        "off_player_3_id",
                                        "off_player_4",
                                        "off_player_4_id",
                                        "off_player_5",
                                        "off_player_5_id",
                                        "def_player_1",
                                        "def_player_1_id",
                                        "def_player_2",
                                        "def_player_2_id",
                                        "def_player_3",
                                        "def_player_3_id",
                                        "def_player_4",
                                        "def_player_4_id",
                                        "def_player_5",
                                        "def_player_5_id",
                                        "points_made",
                                        "home_team_abbrev",
                                        "event_team_abbrev",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                )
                            ]
                        )

                    elif (
                        df.loc[df.index[-1], "event_team"]
                        == df.loc[df.index[-1], "home_team_abbrev"]
                    ):
                        row_df = pd.concat(
                            [
                                df.loc[
                                    df.index[-1], "home_player_1":"away_player_5_id"
                                ],
                                df.loc[
                                    df.index[-1],
                                    [
                                        "points_made_y",
                                        "home_team_abbrev",
                                        "event_team",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                ],
                            ]
                        )

                        parsed_list.extend(
                            [
                                pd.DataFrame(
                                    [list(row_df)],
                                    columns=[
                                        "def_player_1",
                                        "def_player_1_id",
                                        "def_player_2",
                                        "def_player_2_id",
                                        "def_player_3",
                                        "def_player_3_id",
                                        "def_player_4",
                                        "def_player_4_id",
                                        "def_player_5",
                                        "def_player_5_id",
                                        "off_player_1",
                                        "off_player_1_id",
                                        "off_player_2",
                                        "off_player_2_id",
                                        "off_player_3",
                                        "off_player_3_id",
                                        "off_player_4",
                                        "off_player_4_id",
                                        "off_player_5",
                                        "off_player_5_id",
                                        "points_made",
                                        "home_team_abbrev",
                                        "event_team_abbrev",
                                        "away_team_abbrev",
                                        "home_team_id",
                                        "away_team_id",
                                        "game_id",
                                        "game_date",
                                        "season",
                                    ],
                                )
                            ]
                        )

            elif df.loc[df.index[-1], "event_type_de"] in ["shot", "free-throw"]:
                if (
                    df.loc[df.index[-1], "event_team"]
                    == df.loc[df.index[-1], "home_team_abbrev"]
                ):
                    row_df = pd.concat(
                        [
                            df.loc[df.index[-1], "home_player_1":"away_player_5_id"],
                            df.loc[
                                df.index[-1],
                                [
                                    "points_made_y",
                                    "home_team_abbrev",
                                    "event_team",
                                    "away_team_abbrev",
                                    "home_team_id",
                                    "away_team_id",
                                    "game_id",
                                    "game_date",
                                    "season",
                                ],
                            ],
                        ]
                    )

                    parsed_list.extend(
                        [
                            pd.DataFrame(
                                [list(row_df)],
                                columns=[
                                    "off_player_1",
                                    "off_player_1_id",
                                    "off_player_2",
                                    "off_player_2_id",
                                    "off_player_3",
                                    "off_player_3_id",
                                    "off_player_4",
                                    "off_player_4_id",
                                    "off_player_5",
                                    "off_player_5_id",
                                    "def_player_1",
                                    "def_player_1_id",
                                    "def_player_2",
                                    "def_player_2_id",
                                    "def_player_3",
                                    "def_player_3_id",
                                    "def_player_4",
                                    "def_player_4_id",
                                    "def_player_5",
                                    "def_player_5_id",
                                    "points_made",
                                    "home_team_abbrev",
                                    "event_team_abbrev",
                                    "away_team_abbrev",
                                    "home_team_id",
                                    "away_team_id",
                                    "game_id",
                                    "game_date",
                                    "season",
                                ],
                            )
                        ]
                    )
                elif (
                    df.loc[df.index[-1], "event_team"]
                    == df.loc[df.index[-1], "away_team_abbrev"]
                ):
                    row_df = pd.concat(
                        [
                            df.loc[df.index[-1], "home_player_1":"away_player_5_id"],
                            df.loc[
                                df.index[-1],
                                [
                                    "points_made_y",
                                    "home_team_abbrev",
                                    "event_team",
                                    "away_team_abbrev",
                                    "home_team_id",
                                    "away_team_id",
                                    "game_id",
                                    "game_date",
                                    "season",
                                ],
                            ],
                        ]
                    )

                    parsed_list.extend(
                        [
                            pd.DataFrame(
                                [list(row_df)],
                                columns=[
                                    "def_player_1",
                                    "def_player_1_id",
                                    "def_player_2",
                                    "def_player_2_id",
                                    "def_player_3",
                                    "def_player_3_id",
                                    "def_player_4",
                                    "def_player_4_id",
                                    "def_player_5",
                                    "def_player_5_id",
                                    "off_player_1",
                                    "off_player_1_id",
                                    "off_player_2",
                                    "off_player_2_id",
                                    "off_player_3",
                                    "off_player_3_id",
                                    "off_player_4",
                                    "off_player_4_id",
                                    "off_player_5",
                                    "off_player_5_id",
                                    "points_made",
                                    "home_team_abbrev",
                                    "event_team_abbrev",
                                    "away_team_abbrev",
                                    "home_team_id",
                                    "away_team_id",
                                    "game_id",
                                    "game_date",
                                    "season",
                                ],
                            )
                        ]
                    )

        return parsed_list

    def rapm_possessions(self):
        """
        method to extract out all the rapm possessions to be able to run a RAPM
        regression on later
        """

        pbp_df = self.df.copy()
        points_by_second = (
            pbp_df.groupby(["game_id", "seconds_elapsed"])["points_made"]
            .sum()
            .reset_index()
        )
        pbp_df = pbp_df.merge(points_by_second, on=["game_id", "seconds_elapsed"])

        poss_index = pbp_df[
            (self.df.home_possession == 1) | (self.df.away_possession == 1)
        ].index
        shift_dfs = []
        past_index = 0

        for i in poss_index:
            shift_dfs.extend([pbp_df.iloc[past_index + 1 : i + 1, :].reset_index()])
            past_index = i

        poss_df = pd.concat(self.parse_possessions(shift_dfs), sort=True)

        return poss_df

    def playerbygamestats(self):
        """
        this function combines all playerbygamestats and returns a dataframe
        containing them
        """
        points = self._point_calc_player()
        blocks = self._block_calc_player()
        assists = self._assist_calc_player()
        rebounds = self._rebound_calc_player()
        turnovers = self._turnover_calc_player()
        fouls = self._foul_calc_player()
        steals = self._steal_calc_player()
        plus_minus = self._plus_minus_calc_player()
        toc = self._toc_calc_player()
        poss = self._poss_calc_player()

        pbg = toc.merge(
            points, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        pbg = pbg.merge(
            blocks, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        pbg = pbg.merge(
            assists, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        pbg = pbg.merge(rebounds, how="left", on=["player_id", "game_date", "game_id"])
        pbg = pbg.merge(
            turnovers, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        pbg = pbg.merge(
            fouls, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        pbg = pbg.merge(
            steals, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        pbg = pbg.merge(
            plus_minus, how="left", on=["player_id", "team_id", "game_date", "game_id"]
        )
        pbg = pbg.merge(poss, how="left", on=["player_id", "team_id", "game_id"])

        pbg["blk"] = pbg["blk"].fillna(0).astype(int)
        pbg["ast"] = pbg["ast"].fillna(0).astype(int)
        pbg["dreb"] = pbg["dreb"].fillna(0).astype(int)
        pbg["oreb"] = pbg["oreb"].fillna(0).astype(int)
        pbg["tov"] = pbg["tov"].fillna(0).astype(int)
        pbg["pf"] = pbg["pf"].fillna(0).astype(int)
        pbg["stl"] = pbg["stl"].fillna(0).astype(int)
        pbg["fgm"] = pbg["fgm"].fillna(0).astype(int)
        pbg["fga"] = pbg["fga"].fillna(0).astype(int)
        pbg["tpm"] = pbg["tpm"].fillna(0).astype(int)
        pbg["tpa"] = pbg["tpa"].fillna(0).astype(int)
        pbg["ftm"] = pbg["ftm"].fillna(0).astype(int)
        pbg["fta"] = pbg["fta"].fillna(0).astype(int)
        pbg["is_home"] = np.where(pbg["team_id"] == self.home_team_id, 1, 0)
        pbg["team_abbrev"] = np.where(
            self.home_team_id == pbg["team_id"], self.home_team, self.away_team
        )
        pbg["opponent"] = np.where(
            pbg["team_id"] == self.home_team_id, self.away_team_id, self.home_team_id
        )
        pbg["opponent_abbrev"] = np.where(
            pbg["team_id"] == self.home_team_id, self.away_team, self.home_team
        )
        pbg["season"] = self.season
        pbg["player_id"] = pbg["player_id"].astype(int)
        pbg = pbg[pbg["toc"] > 0]

        return pbg

    def teambygamestats(self):
        """
        main team stats calc hook
        """

        points = self._point_calc_team()
        blocks = self._block_calc_team()
        assists = self._assist_calc_team()
        rebounds = self._rebound_calc_team()
        turnovers = self._turnover_calc_team()
        fouls = self._foul_calc_team()
        steals = self._steal_calc_team()
        plus_minus = self._plus_minus_team()
        poss = self._poss_calc_team()

        tbg = points.merge(blocks, how="left", on=["team_id", "game_id"])

        tbg = tbg.merge(assists, how="left", on=["team_id", "game_id"])
        tbg = tbg.merge(rebounds, how="left", on=["team_id", "game_id"])
        tbg = tbg.merge(turnovers, how="left", on=["team_id", "game_id"])
        tbg = tbg.merge(fouls, how="left", on=["team_id", "game_id"])
        tbg = tbg.merge(steals, how="left", on=["team_id", "game_id"])
        tbg = tbg.merge(plus_minus, how="left", on=["team_id", "game_id"])
        tbg = tbg.merge(poss, how="left", on=["team_id", "game_id"])
        tbg["game_date"] = self.df["game_date"].unique()[0]
        tbg["season"] = self.df["season"].unique()[0]
        tbg["toc"] = self.df["seconds_elapsed"].max()
        tbg[
            "toc_string"
        ] = f"{math.floor(self.df['seconds_elapsed'].max()/60)}:{self.df['seconds_elapsed'].max()%60}0"
        tbg["is_home"] = np.where(
            tbg["team_id"] == self.df["home_team_id"].unique()[0], 1, 0
        )
        tbg["is_win"] = np.where(tbg["points_for"] > tbg["points_against"], 1, 0)

        tbg["blk"] = tbg["blk"].fillna(0).astype(int)
        tbg["ast"] = tbg["ast"].fillna(0).astype(int)
        tbg["dreb"] = tbg["dreb"].fillna(0).astype(int)
        tbg["oreb"] = tbg["oreb"].fillna(0).astype(int)
        tbg["tov"] = tbg["tov"].fillna(0).astype(int)
        tbg["pf"] = tbg["pf"].fillna(0).astype(int)
        tbg["stl"] = tbg["stl"].fillna(0).astype(int)
        tbg["fgm"] = tbg["fgm"].fillna(0).astype(int)
        tbg["fga"] = tbg["fga"].fillna(0).astype(int)
        tbg["tpm"] = tbg["tpm"].fillna(0).astype(int)
        tbg["tpa"] = tbg["tpa"].fillna(0).astype(int)
        tbg["ftm"] = tbg["ftm"].fillna(0).astype(int)
        tbg["fta"] = tbg["fta"].fillna(0).astype(int)
        tbg["opponent"] = np.where(
            tbg["team_id"] == self.home_team_id, self.away_team_id, self.home_team_id
        )
        tbg["opponent_abbrev"] = np.where(
            tbg["team_id"] == self.home_team_id, self.away_team, self.home_team
        )

        return tbg
