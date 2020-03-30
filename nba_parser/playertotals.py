import pandas as pd
import numpy as np
from sklearn.linear_model import RidgeCV


class PlayerTotals:
    """
    This class is used to calculate player totals from a list of
    dataframes. The dataframes have to be created by PbP.playerbygamestats()
    or else the methods won't work. I've grouped these stat calculations in a
    seperate class because they work best with larger sample sizes
    """

    def __init__(self, pbg_list):
        self.pbg = pd.concat(pbg_list)

    def player_advanced_stats(self):

        stats = [
            "toc",
            "fgm",
            "fga",
            "tpm",
            "tpa",
            "ftm",
            "fta",
            "blk",
            "ast",
            "oreb",
            "dreb",
            "tov",
            "pf",
            "stl",
            "plus",
            "minus",
            "plus_minus",
            "possessions",
            "points",
        ]
        grouped_df = (
            self.pbg.groupby(["player_id", "player_name"])[stats].sum().reset_index()
        )
        # equivalent of select distinct
        team_df = self.pbg[
            ["player_id", "player_name", "team_abbrev"]
        ].drop_duplicates()

        team_df = (
            self.pbg.groupby(["player_id", "player_name"])
            .agg({"team_abbrev": lambda x: "/".join(x.unique())})
            .reset_index()
        )

        gp_df = (
            self.pbg.groupby(["player_id", "player_name"])["game_id"]
            .count()
            .reset_index()
            .rename(columns={"game_id": "gp"})
        )
        grouped_df = grouped_df.merge(gp_df, on=["player_id", "player_name"])
        grouped_df = grouped_df.merge(team_df, on=["player_id", "player_name"])
        grouped_df["off_rating"] = (grouped_df["plus"] * 100) / grouped_df[
            "possessions"
        ]
        grouped_df["def_rating"] = (grouped_df["minus"] * 100) / grouped_df[
            "possessions"
        ]
        grouped_df["efg_percent"] = round(
            ((grouped_df["fgm"] + 0.5 * grouped_df["tpm"]) / grouped_df["fga"]) * 100, 1
        )
        grouped_df["ts_percent"] = round(
            (
                grouped_df["points"]
                / (2 * (grouped_df["fga"] + (0.44 * grouped_df["fta"])))
            )
            * 100,
            1,
        )
        grouped_df["oreb_percent"] = round(
            (grouped_df["oreb"] / grouped_df["possessions"]) * 100, 1
        )
        grouped_df["dreb_percent"] = round(
            (grouped_df["dreb"] / grouped_df["possessions"]) * 100, 1
        )
        grouped_df["ast_percent"] = round(
            (grouped_df["ast"] / grouped_df["possessions"]) * 100, 1
        )
        grouped_df["blk_percent"] = round(
            (grouped_df["blk"] / grouped_df["possessions"]) * 100, 1
        )
        grouped_df["stl_percent"] = round(
            (grouped_df["stl"] / grouped_df["possessions"]) * 100, 1
        )
        grouped_df["tov_percent"] = round(
            (grouped_df["tov"] / grouped_df["possessions"]) * 100, 1
        )
        grouped_df["usg_percent"] = round(
            (
                (grouped_df["tov"] + grouped_df["fga"] + (0.44 * grouped_df["fta"]))
                / grouped_df["possessions"]
            )
            * 100,
            1,
        )

        grouped_df["min_season"] = self.pbg["season"].min()
        grouped_df["max_season"] = self.pbg["season"].max()

        return grouped_df

    @staticmethod
    def rapm_matrix_map(row_in, players):
        p1 = row_in[0]
        p2 = row_in[1]
        p3 = row_in[2]
        p4 = row_in[3]
        p5 = row_in[4]
        p6 = row_in[5]
        p7 = row_in[6]
        p8 = row_in[7]
        p9 = row_in[8]
        p10 = row_in[9]

        rowOut = np.zeros([(len(players) * 2) + 1])

        rowOut[players.index(p1)] = 1
        rowOut[players.index(p2)] = 1
        rowOut[players.index(p3)] = 1
        rowOut[players.index(p4)] = 1
        rowOut[players.index(p5)] = 1

        rowOut[players.index(p6) + len(players)] = -1
        rowOut[players.index(p7) + len(players)] = -1
        rowOut[players.index(p8) + len(players)] = -1
        rowOut[players.index(p9) + len(players)] = -1
        rowOut[players.index(p10) + len(players)] = -1

        rowOut[len(players) + 1] = row_in[10]

        return rowOut

    @staticmethod
    def player_rapm_results(rapm_shifts):
        """
        funciton to produce RAPM coefficients for players in the
        rapm shifts passed to the function
        """

        def lambda_to_alpha(lambda_value, samples):
            return (lambda_value * samples) / 2.0

        def player_details(rapm_shifts):
            """
            function to get player_id, player_name kvp in a dataframe
            to join to rapm output to get names for player_ids
            """
            off_player_1 = rapm_shifts[
                ["off_player_1_id", "off_player_1"]
            ].drop_duplicates()
            off_player_2 = rapm_shifts[
                ["off_player_2_id", "off_player_2"]
            ].drop_duplicates()
            off_player_3 = rapm_shifts[
                ["off_player_3_id", "off_player_3"]
            ].drop_duplicates()
            off_player_4 = rapm_shifts[
                ["off_player_4_id", "off_player_4"]
            ].drop_duplicates()
            off_player_5 = rapm_shifts[
                ["off_player_5_id", "off_player_5"]
            ].drop_duplicates()
            off_player_1 = off_player_1.rename(
                columns={"off_player_1_id": "player_id", "off_player_1": "player_name"}
            )
            off_player_2 = off_player_2.rename(
                columns={"off_player_2_id": "player_id", "off_player_2": "player_name"}
            )
            off_player_3 = off_player_3.rename(
                columns={"off_player_3_id": "player_id", "off_player_3": "player_name"}
            )
            off_player_4 = off_player_4.rename(
                columns={"off_player_4_id": "player_id", "off_player_4": "player_name"}
            )
            off_player_5 = off_player_5.rename(
                columns={"off_player_5_id": "player_id", "off_player_5": "player_name"}
            )
            def_player_1 = rapm_shifts[
                ["def_player_1_id", "def_player_1"]
            ].drop_duplicates()
            def_player_2 = rapm_shifts[
                ["def_player_2_id", "def_player_2"]
            ].drop_duplicates()
            def_player_3 = rapm_shifts[
                ["def_player_3_id", "def_player_3"]
            ].drop_duplicates()
            def_player_4 = rapm_shifts[
                ["def_player_4_id", "def_player_4"]
            ].drop_duplicates()
            def_player_5 = rapm_shifts[
                ["def_player_5_id", "def_player_5"]
            ].drop_duplicates()
            def_player_1 = def_player_1.rename(
                columns={"def_player_1_id": "player_id", "def_player_1": "player_name"}
            )
            def_player_2 = def_player_2.rename(
                columns={"def_player_2_id": "player_id", "def_player_2": "player_name"}
            )
            def_player_3 = def_player_3.rename(
                columns={"def_player_3_id": "player_id", "def_player_3": "player_name"}
            )
            def_player_4 = def_player_4.rename(
                columns={"def_player_4_id": "player_id", "def_player_4": "player_name"}
            )
            def_player_5 = def_player_5.rename(
                columns={"def_player_5_id": "player_id", "def_player_5": "player_name"}
            )
            players = pd.concat(
                [
                    off_player_1,
                    off_player_2,
                    off_player_3,
                    off_player_4,
                    off_player_5,
                    def_player_1,
                    def_player_2,
                    def_player_3,
                    def_player_4,
                    def_player_5,
                ]
            )
            players = players.drop_duplicates()

            return players

        players = list(
            set(
                list(rapm_shifts["off_player_1_id"].unique())
                + list(rapm_shifts["off_player_2_id"].unique())
                + list(rapm_shifts["off_player_3_id"].unique())
                + list(rapm_shifts["off_player_4_id"].unique())
                + list(rapm_shifts["off_player_5_id"].unique())
                + list(rapm_shifts["def_player_1_id"].unique())
                + list(rapm_shifts["def_player_2_id"].unique())
                + list(rapm_shifts["def_player_3_id"].unique())
                + list(rapm_shifts["def_player_4_id"].unique())
                + list(rapm_shifts["def_player_5_id"].unique())
            )
        )

        players.sort()

        player_df = player_details(rapm_shifts)
        rapm_shifts["points_per_100_poss"] = rapm_shifts["points_made"] * 100
        rapm_shifts["possessions"] = 1
        rapm_shifts["is_home"] = np.where(
            rapm_shifts["home_team_abbrev"] == rapm_shifts["event_team_abbrev"], 1, 0
        )
        train_x = rapm_shifts[
            [
                "off_player_1_id",
                "off_player_2_id",
                "off_player_3_id",
                "off_player_4_id",
                "off_player_5_id",
                "def_player_1_id",
                "def_player_2_id",
                "def_player_3_id",
                "def_player_4_id",
                "def_player_5_id",
                "is_home",
            ]
        ].to_numpy()

        train_x = np.apply_along_axis(PlayerTotals.rapm_matrix_map, 1, train_x, players)
        train_y = rapm_shifts[["points_per_100_poss"]].to_numpy()
        possessions = rapm_shifts["possessions"]

        lambdas_rapm = [0.01, 0.05, 0.1]
        alphas = [lambda_to_alpha(l, train_x.shape[0]) for l in lambdas_rapm]
        clf = RidgeCV(alphas=alphas, cv=5, fit_intercept=True, normalize=False)
        model = clf.fit(train_x, train_y, sample_weight=possessions)
        player_arr = np.transpose(np.array(players).reshape(1, len(players)))

        # extract our coefficients into the offensive and defensive parts
        coef_offensive_array = np.transpose(model.coef_[:, 0 : len(players)])
        coef_defensive_array = np.transpose(model.coef_[:, len(players) : -1])

        # concatenate the offensive and defensive values with the playey ids into a mx3 matrix
        player_id_with_coef = np.concatenate(
            [player_arr, coef_offensive_array, coef_defensive_array], axis=1
        )
        # build a dataframe from our matrix
        players_coef = pd.DataFrame(player_id_with_coef)
        intercept = model.intercept_
        name = "rapm"
        # apply new column names
        players_coef.columns = [
            "player_id",
            f"{name}_off",
            f"{name}_def",
        ]
        # Add the offesnive and defensive components together (we should really be weighing this to the number of offensive and defensive possession played as they are often not equal).
        players_coef[name] = players_coef[f"{name}_off"] + players_coef[f"{name}_def"]

        # rank the values
        players_coef[f"{name}_rank"] = players_coef[name].rank(ascending=False)
        players_coef[f"{name}_off_rank"] = players_coef[f"{name}_off"].rank(
            ascending=False
        )
        players_coef[f"{name}_def_rank"] = players_coef[f"{name}_def"].rank(
            ascending=False
        )

        # add the intercept for reference
        players_coef[f"{name}_intercept"] = intercept[0]

        results_df = players_coef.merge(
            player_df[["player_id", "player_name"]], on="player_id"
        )
        results_df = np.round(results_df, decimals=2)
        results_df["min_season"] = rapm_shifts["season"].min()
        results_df["max_season"] = rapm_shifts["season"].max()

        return results_df
