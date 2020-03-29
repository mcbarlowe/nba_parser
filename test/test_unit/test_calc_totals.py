import pytest
import pandas as pd
import nba_parser as npar


@pytest.fixture
def setup(scope="module"):
    """
    function for test setup and teardown
    """
    files = [
        "21900002.csv",
        "21900025.csv",
        "21900040.csv",
        "21900054.csv",
        "21900074.csv",
        "21900088.csv",
        "21900100.csv",
        "21900126.csv",
        "21900139.csv",
        "21900151.csv",
    ]
    pbp_dfs = [pd.read_csv(f"test/{f}") for f in files]
    pbp_dfs = [npar.PbP(pbp_df) for pbp_df in pbp_dfs]
    pbg_dfs = [pbp_df.playerbygamestats() for pbp_df in pbp_dfs]
    # TODO add multiple files here to make the tests more random and more
    # robust Matt Barlowe 2020-03-24
    yield pbg_dfs


def test_player_advanced_stats(setup):
    """
    test to make sure the advanced stats are calculating properly
    when grouping things together
    """

    pbp_list = setup

    player_totals = npar.PlayerTotals(pbp_list)
    player_totals = player_totals.player_advanced_stats()

    assert player_totals.loc[player_totals["player_id"] == 2544, "fgm"].values[0] == 88
    assert player_totals.loc[player_totals["player_id"] == 2544, "gp"].values[0] == 10
    assert player_totals.loc[player_totals["player_id"] == 2544, "fga"].values[0] == 187
    assert player_totals.loc[player_totals["player_id"] == 2544, "tpm"].values[0] == 16
    assert player_totals.loc[player_totals["player_id"] == 2544, "tpa"].values[0] == 51
    assert player_totals.loc[player_totals["player_id"] == 2544, "ftm"].values[0] == 48
    assert player_totals.loc[player_totals["player_id"] == 2544, "fta"].values[0] == 69
    assert player_totals.loc[player_totals["player_id"] == 2544, "oreb"].values[0] == 10
    assert player_totals.loc[player_totals["player_id"] == 2544, "dreb"].values[0] == 72
    assert player_totals.loc[player_totals["player_id"] == 2544, "ast"].values[0] == 110
    assert player_totals.loc[player_totals["player_id"] == 2544, "tov"].values[0] == 33
    assert player_totals.loc[player_totals["player_id"] == 2544, "blk"].values[0] == 6
    assert (
        player_totals.loc[player_totals["player_id"] == 2544, "plus_minus"].values[0]
        == 83
    )
    assert (
        player_totals.loc[player_totals["player_id"] == 2544, "team_abbrev"].values[0]
        == "LAL"
    )
    assert player_totals.loc[player_totals["player_id"] == 2544, "efg_percent"].values[0] == 51.3
