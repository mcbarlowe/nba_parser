import pandas as pd


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
            teams_df.groupby(["team_id", "team_abbrev", "season"])[
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
        print(team_advanced_stats)

        return team_advanced_stats
