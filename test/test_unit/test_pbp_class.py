from nba_parser.nba_parser import PbP
import pandas as pd
import pytest


@pytest.fixture
def setup():
    """
    function for test setup and teardown
    """
    pbp_df = pd.read_csv("test/20700233.csv")
    pbp_df["season"] = 2008
    pbp = PbP(pbp_df)
    # TODO add multiple files here to make the tests more random and more
    # robust
    yield pbp


def test_class_build(setup):
    """
    This test makes sure the proper class is instantiated when called
    """

    pbp = setup

    assert isinstance(pbp, PbP)
    assert isinstance(pbp.df, pd.DataFrame)
    assert pbp.home_team == "DEN"
    assert pbp.away_team == "LAC"
    assert pbp.home_team_id == 1610612743
    assert pbp.away_team_id == 1610612746
    assert pbp.game_date.strftime("%Y-%m-%d") == "2007-11-30"
    assert pbp.season == 2008


def test_point_calc_player(setup):
    """
    testing to make sure points, field goals attempted/made, three pointers
    attempted/made, and free throws attempted/made are correct
    """

    pbp = setup

    stats_df = pbp._point_calc_player()

    assert stats_df.loc[stats_df["player_id"] == 1894, "fgm"].values[0] == 10
    assert stats_df.loc[stats_df["player_id"] == 1894, "fga"].values[0] == 20
    assert stats_df.loc[stats_df["player_id"] == 1894, "tpm"].values[0] == 1
    assert stats_df.loc[stats_df["player_id"] == 1894, "tpa"].values[0] == 2
    assert stats_df.loc[stats_df["player_id"] == 1894, "ftm"].values[0] == 5
    assert stats_df.loc[stats_df["player_id"] == 1894, "fta"].values[0] == 6
    assert stats_df.loc[stats_df["player_id"] == 947, "fgm"].values[0] == 11
    assert stats_df.loc[stats_df["player_id"] == 947, "fga"].values[0] == 26
    assert stats_df.loc[stats_df["player_id"] == 947, "tpm"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 947, "tpa"].values[0] == 2
    assert stats_df.loc[stats_df["player_id"] == 947, "ftm"].values[0] == 4
    assert stats_df.loc[stats_df["player_id"] == 947, "fta"].values[0] == 6


def test_block_calc_player(setup):
    """
    testing to make sure block calculations are computing properly
    """

    pbp = setup

    blocks = pbp._block_calc_player()
    stats_df = pbp._point_calc_player()

    # merging with normal player stats to make sure that players with
    # zero block are properly calculated as well

    stats_df = stats_df.merge(
        blocks, how="left", on=["player_id", "team_id", "game_date", "game_id"]
    )
    stats_df["blk"] = stats_df["blk"].fillna(0).astype(int)

    assert stats_df.loc[stats_df["player_id"] == 1894, "blk"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 947, "blk"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 948, "blk"].values[0] == 1
    assert stats_df.loc[stats_df["player_id"] == 2549, "blk"].values[0] == 3
    assert stats_df.loc[stats_df["player_id"] == 2059, "blk"].values[0] == 1


def test_assist_calc_player(setup):
    """
    testing to make sure block calculations are computing properly
    """

    pbp = setup

    assists = pbp._assist_calc_player()
    stats_df = pbp._point_calc_player()

    # merging with normal player stats to make sure that players with
    # zero assists are properly calculated as well

    stats_df = stats_df.merge(
        assists, how="left", on=["player_id", "team_id", "game_date", "game_id"]
    )
    stats_df["ast"] = stats_df["ast"].fillna(0).astype(int)

    assert stats_df.loc[stats_df["player_id"] == 1894, "ast"].values[0] == 5
    assert stats_df.loc[stats_df["player_id"] == 947, "ast"].values[0] == 7
    assert stats_df.loc[stats_df["player_id"] == 948, "ast"].values[0] == 3
    assert stats_df.loc[stats_df["player_id"] == 2549, "ast"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 2059, "ast"].values[0] == 3
