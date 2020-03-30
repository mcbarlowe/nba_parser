import pandas as pd
import numpy as np
from sklearn.linear_model import RidgeCV


class TeamTotals:
    """
    This class is used to calculate team totals from a list of
    dataframes. The dataframes have to be created by PbP.teambygamestats()
    or else the methods won't work. I've grouped these stat calculations in a
    seperate class because they work best with larger sample sizes
    """

    def __init__(self, tbg_list):
        self.tbg = pd.concat(tbg_list)

    def team_advanced_stats(self):

        teams_df = self.tbg.merge(self.tbg, on="game_id", suffixes=["", "_opponent"])
        teams_df = teams_df[teams_df.team_id != teams_df.team_id_opponent]
        team_advanced_stats = (
            teams_df.groupby(["team_id", "team_abbrev"])[
                [
                    "fgm",
                    "tpm",
                    "fga",
                    "points_for",
                    "points_against",
                    "plus_minus",
                    "tpa",
                    "fta",
                    "tov",
                    "dreb",
                    "oreb",
                    "ftm",
                    "ast",
                    "blk",
                    "dreb_opponent",
                    "oreb_opponent",
                    "fgm_opponent",
                    "fga_opponent",
                    "tpm_opponent",
                    "tpa_opponent",
                    "fta_opponent",
                    "ftm_opponent",
                    "tov_opponent",
                    "possessions",
                    "possessions_opponent",
                ]
            ]
            .sum()
            .reset_index()
        )
        gp_df = (
            self.tbg.groupby(["team_id"])["game_id"]
            .count()
            .reset_index()
            .rename(columns={"game_id": "gp"})
        )
        team_advanced_stats = team_advanced_stats.merge(gp_df, on="team_id")
        team_advanced_stats["efg_percentage"] = (
            team_advanced_stats["fgm"] + (0.5 * team_advanced_stats["tpm"])
        ) / team_advanced_stats["fga"]
        team_advanced_stats["true_shooting_percentage"] = team_advanced_stats[
            "points_for"
        ] / (2 * (team_advanced_stats["fga"] + (team_advanced_stats["fta"] * 0.44)))
        team_advanced_stats["tov_percentage"] = 100 * (
            team_advanced_stats["tov"] / team_advanced_stats["possessions"]
        )
        team_advanced_stats["oreb_percentage"] = 100 * (
            team_advanced_stats["oreb"]
            / (team_advanced_stats["oreb"] + team_advanced_stats["dreb_opponent"])
        )
        team_advanced_stats["ft_per_fga"] = (
            team_advanced_stats["ftm"] / team_advanced_stats["fta"]
        )
        team_advanced_stats["opp_efg_percentage"] = (
            team_advanced_stats["fgm_opponent"]
            + (0.5 * team_advanced_stats["tpm_opponent"])
        ) / team_advanced_stats["fga_opponent"]
        team_advanced_stats["opp_tov_percentage"] = 100 * (
            team_advanced_stats["tov_opponent"]
            / team_advanced_stats["possessions_opponent"]
        )
        team_advanced_stats["dreb_percentage"] = 100 * (
            team_advanced_stats["dreb"]
            / (team_advanced_stats["oreb_opponent"] + team_advanced_stats["dreb"])
        )
        team_advanced_stats["opp_ft_per_fga"] = (
            team_advanced_stats["ftm_opponent"] / team_advanced_stats["fta_opponent"]
        )
        team_advanced_stats["off_rating"] = (
            team_advanced_stats["points_for"] / team_advanced_stats["possessions"] * 100
        )
        team_advanced_stats["def_rating"] = (
            team_advanced_stats["points_against"]
            / team_advanced_stats["possessions"]
            * 100
        )
        team_advanced_stats["min_season"] = self.tbg["season"].min()
        team_advanced_stats["max_season"] = self.tbg["season"].max()

        return team_advanced_stats

    @staticmethod
    def rapm_matrix_map(row_in, teams):
        """
        function that rearranges the team rapm matrix to make it ready to pass
        to the Ridge Regression
        """

        team1 = row_in[0]
        team2 = row_in[1]

        rowout = np.zeros([(len(teams) * 2) + 1])

        rowout[teams.index(team1)] = 1
        rowout[teams.index(team2) + len(teams)] = -1
        rowout[-1] = row_in[-1]

        return rowout

    def _rapm_matrix_creation(self):
        """
        function to create train_x and train_y matrices for input into a Ridge
        regression
        """
        self.tbg["points_per_100_poss"] = (
            self.tbg["points_for"] / self.tbg["possessions"]
        ) * 100

        teams = list(self.tbg["team_id"].unique())
        teams.sort()

        train_x = self.tbg[["team_id", "opponent", "is_home"]].to_numpy()
        train_x = np.apply_along_axis(TeamTotals.rapm_matrix_map, 1, train_x, teams)
        train_y = self.tbg[["points_per_100_poss"]].to_numpy()

        return train_x, train_y

    def team_rapm_results(self):
        """
        function will return RAPM regression results based on the the teambygamestats()
        results passed to the TeamTotals object when instantiated
        """

        def lambda_to_alpha(lambda_value, samples):
            return (lambda_value * samples) / 2.0

        train_x, train_y = self._rapm_matrix_creation()
        possessions = self.tbg["possessions"]
        teams = list(self.tbg["team_id"].unique())
        teams.sort()
        lambdas_rapm = [0.01, 0.05, 0.1]
        alphas = [lambda_to_alpha(l, train_x.shape[0]) for l in lambdas_rapm]
        clf = RidgeCV(alphas=alphas, cv=5, fit_intercept=True, normalize=False)
        model = clf.fit(train_x, train_y, sample_weight=possessions)
        team_arr = np.transpose(np.array(teams).reshape(1, len(teams)))

        # extract our coefficients into the offensive and defensive parts
        coef_offensive_array = np.transpose(model.coef_[:, 0 : len(teams)])
        coef_defensive_array = np.transpose(model.coef_[:, len(teams) : -1])

        # concatenate the offensive and defensive values with the playey ids into a mx3 matrix
        team_id_with_coef = np.concatenate(
            [team_arr, coef_offensive_array, coef_defensive_array], axis=1
        )
        # build a dataframe from our matrix
        teams_coef = pd.DataFrame(team_id_with_coef)
        intercept = model.intercept_
        name = "rapm"
        # apply new column names
        teams_coef.columns = ["team_id", f"{name}_off", f"{name}_def"]
        # Add the offesnive and defensive components together (we should really be weighing this to the number of offensive and defensive possession played as they are often not equal).
        teams_coef[name] = teams_coef[f"{name}_off"] + teams_coef[f"{name}_def"]

        # rank the values
        teams_coef[f"{name}_rank"] = teams_coef[name].rank(ascending=False)
        teams_coef[f"{name}_off_rank"] = teams_coef[f"{name}_off"].rank(ascending=False)
        teams_coef[f"{name}_def_rank"] = teams_coef[f"{name}_def"].rank(ascending=False)

        # add the intercept for reference
        teams_coef[f"{name}_intercept"] = intercept[0]

        results_df = teams_coef.merge(
            self.tbg[["team_id", "team_abbrev"]].drop_duplicates(), on="team_id"
        )

        results_df["team_id"] = results_df["team_id"].astype(int)
        results_df["min_season"] = self.tbg["season"].min()
        results_df["max_season"] = self.tbg["season"].max()
        results_df = np.round(results_df, decimals=2)

        return results_df
