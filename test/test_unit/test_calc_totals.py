import pytest
import pandas as pd
import nba_parser as npar


@pytest.fixture(scope="session")
def setup():
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
    tbg_dfs = [pbp_df.teambygamestats() for pbp_df in pbp_dfs]

    yield pbg_dfs, tbg_dfs, pbp_dfs


def test_player_advanced_stats(setup):
    """
    test to make sure the advanced stats are calculating properly
    when grouping things together
    """

    pbp_list, _, _ = setup

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
        player_totals.loc[player_totals["player_id"] == 2544, "points"].values[0] == 240
    )
    assert (
        player_totals.loc[player_totals["player_id"] == 2544, "plus_minus"].values[0]
        == 83
    )
    assert (
        player_totals.loc[player_totals["player_id"] == 2544, "team_abbrev"].values[0]
        == "LAL"
    )
    assert (
        player_totals.loc[player_totals["player_id"] == 2544, "efg_percent"].values[0]
        == 51.3
    )
    assert (
        player_totals.loc[player_totals["player_id"] == 2544, "ts_percent"].values[0]
        == 55.2
    )


def test_team_advanced_stats(setup):
    """
    test to make sure the advanced stats are calculating properly
    when grouping things together
    """

    _, tbg_list, _ = setup

    team_totals = npar.TeamTotals(tbg_list)
    team_totals = team_totals.team_advanced_stats()

    assert team_totals.loc[team_totals["team_id"] == 1610612747, "fgm"].values[0] == 426
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "gp"].values[0] == 10
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "fga"].values[0] == 903
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "tpm"].values[0] == 93
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "tpa"].values[0] == 292
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "ftm"].values[0] == 154
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "fta"].values[0] == 210
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "oreb"].values[0] == 97
    assert (
        team_totals.loc[team_totals["team_id"] == 1610612747, "dreb"].values[0] == 366
    )
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "ast"].values[0] == 265
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "tov"].values[0] == 142
    assert team_totals.loc[team_totals["team_id"] == 1610612747, "blk"].values[0] == 75
    assert (
        team_totals.loc[team_totals["team_id"] == 1610612747, "points_for"].values[0]
        == 1099
    )
    assert (
        team_totals.loc[team_totals["team_id"] == 1610612747, "plus_minus"].values[0]
        == 83
    )


def test_team_rapm(setup):
    """
    test to make sure rapm code runs properly
    """
    _, tbg_list, _ = setup

    team_totals = npar.TeamTotals(tbg_list)
    team_rapm = team_totals.team_rapm_results()

    print(team_rapm)


def test_player_rapm(setup):
    """
    test to make sure rapm code runs properly
    """
    _, _, pbp_list = setup

    rapm_possession = pd.concat([x.rapm_possessions() for x in pbp_list])
    print(rapm_possession)
    player_rapm = npar.PlayerTotals.player_rapm_results(rapm_possession)

    print(player_rapm)
