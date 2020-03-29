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

        return grouped_df
