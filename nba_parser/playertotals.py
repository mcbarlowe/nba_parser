import pandas as pd


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
        grouped_df["efg_percent"] = round(((
            grouped_df["fgm"] + 0.5 * grouped_df["tpm"]
        ) / grouped_df["fga"])  * 100, 1)

        print(grouped_df)

        return grouped_df
