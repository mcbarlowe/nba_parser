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

    def _rebound_calc_player(self):
        """
        function to calculate player's offensive and defensive rebound totals
        """
        rebounds = (
            self.df.groupby(["player1_id", "game_id", "game_date", "player1_team_id"])[
                ["is_o_rebound", "is_d_rebound"]
            ]
            .sum()
            .reset_index()
        )

        rebounds["game_date"] = pd.to_datetime(rebounds["game_date"])
        rebounds["player1_team_id"] = rebounds["player1_team_id"].astype(int)
        rebounds.rename(
            columns={
                "player1_id": "player_id",
                "player1_team_id": "team_id",
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

        turnovers["game_date"] = pd.to_datetime(turnovers["game_date"])
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
        fouls["game_date"] = pd.to_datetime(fouls["game_date"])
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

        steals["game_date"] = pd.to_datetime(steals["game_date"])
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

        total_plus_minus["game_date"] = pd.to_datetime(total_plus_minus["game_date"])
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
