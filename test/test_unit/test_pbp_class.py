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
    # robust Matt Barlowe 2020-03-24
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


def test_rebound_calc_player(setup):
    """
    testing to make sure block calculations are computing properly
    """

    pbp = setup

    rebounds = pbp._rebound_calc_player()
    stats_df = pbp._point_calc_player()

    # merging with normal player stats to make sure that players with
    # zero assists are properly calculated as well

    stats_df = stats_df.merge(
        rebounds, how="left", on=["player_id", "team_id", "game_date", "game_id"]
    )
    stats_df["dreb"] = stats_df["dreb"].fillna(0).astype(int)
    stats_df["oreb"] = stats_df["oreb"].fillna(0).astype(int)

    assert stats_df.loc[stats_df["player_id"] == 1894, "dreb"].values[0] == 2
    assert stats_df.loc[stats_df["player_id"] == 947, "dreb"].values[0] == 3
    assert stats_df.loc[stats_df["player_id"] == 948, "dreb"].values[0] == 8
    assert stats_df.loc[stats_df["player_id"] == 2549, "dreb"].values[0] == 6
    assert stats_df.loc[stats_df["player_id"] == 2059, "dreb"].values[0] == 4

    assert stats_df.loc[stats_df["player_id"] == 1894, "oreb"].values[0] == 2
    assert stats_df.loc[stats_df["player_id"] == 947, "oreb"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 948, "oreb"].values[0] == 4
    assert stats_df.loc[stats_df["player_id"] == 2549, "oreb"].values[0] == 3
    assert stats_df.loc[stats_df["player_id"] == 2059, "oreb"].values[0] == 2


def test_steal_calc_player(setup):
    """
    testing to make sure steal calculations are correct
    """
    pbp = setup

    steals = pbp._steal_calc_player()
    stats_df = pbp._point_calc_player()

    stats_df = stats_df.merge(
        steals, how="left", on=["player_id", "team_id", "game_date", "game_id"]
    )
    stats_df["stl"] = stats_df["stl"].fillna(0).astype(int)

    assert stats_df.loc[stats_df["player_id"] == 1894, "stl"].values[0] == 2
    assert stats_df.loc[stats_df["player_id"] == 947, "stl"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 948, "stl"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 2549, "stl"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 2059, "stl"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 1510, "stl"].values[0] == 2
    assert stats_df.loc[stats_df["player_id"] == 2546, "stl"].values[0] == 3


def test_turnover_calc_player(setup):
    """
    testing to make sure steal calculations are correct
    """
    pbp = setup

    turnovers = pbp._turnover_calc_player()
    stats_df = pbp._point_calc_player()

    stats_df = stats_df.merge(
        turnovers, how="left", on=["player_id", "team_id", "game_date", "game_id"]
    )
    stats_df["tov"] = stats_df["tov"].fillna(0).astype(int)

    assert stats_df.loc[stats_df["player_id"] == 1894, "tov"].values[0] == 6
    assert stats_df.loc[stats_df["player_id"] == 947, "tov"].values[0] == 4
    assert stats_df.loc[stats_df["player_id"] == 948, "tov"].values[0] == 1
    assert stats_df.loc[stats_df["player_id"] == 2549, "tov"].values[0] == 4
    assert stats_df.loc[stats_df["player_id"] == 2059, "tov"].values[0] == 3
    assert stats_df.loc[stats_df["player_id"] == 1510, "tov"].values[0] == 1
    assert stats_df.loc[stats_df["player_id"] == 2546, "tov"].values[0] == 4


def test_foul_calc_player(setup):
    """
    testing to make sure personal foul calculations are correct
    """
    pbp = setup

    fouls = pbp._foul_calc_player()
    stats_df = pbp._point_calc_player()

    stats_df = stats_df.merge(
        fouls, how="left", on=["player_id", "team_id", "game_date", "game_id"]
    )
    stats_df["pf"] = stats_df["pf"].fillna(0).astype(int)

    assert stats_df.loc[stats_df["player_id"] == 1894, "pf"].values[0] == 4
    assert stats_df.loc[stats_df["player_id"] == 947, "pf"].values[0] == 0
    assert stats_df.loc[stats_df["player_id"] == 948, "pf"].values[0] == 4
    assert stats_df.loc[stats_df["player_id"] == 2549, "pf"].values[0] == 5
    assert stats_df.loc[stats_df["player_id"] == 2059, "pf"].values[0] == 5
    assert stats_df.loc[stats_df["player_id"] == 1510, "pf"].values[0] == 5
    assert stats_df.loc[stats_df["player_id"] == 2546, "pf"].values[0] == 4


def test_plus_minus_calc_player(setup):
    """
    testing to make sure personal foul calculations are correct
    """
    pbp = setup

    plus_minus = pbp._plus_minus_calc_player()
    stats_df = pbp._point_calc_player()

    stats_df = stats_df.merge(
        plus_minus, how="left", on=["player_id", "team_id", "game_date", "game_id"]
    )
    stats_df["plus_minus"] = stats_df["plus_minus"].fillna(0).astype(int)

    assert stats_df.loc[stats_df["player_id"] == 1894, "plus_minus"].values[0] == -8
    assert stats_df.loc[stats_df["player_id"] == 947, "plus_minus"].values[0] == 16
    assert stats_df.loc[stats_df["player_id"] == 948, "plus_minus"].values[0] == 18
    assert stats_df.loc[stats_df["player_id"] == 2549, "plus_minus"].values[0] == -9
    assert stats_df.loc[stats_df["player_id"] == 2059, "plus_minus"].values[0] == 6
    assert stats_df.loc[stats_df["player_id"] == 1510, "plus_minus"].values[0] == -12
    assert stats_df.loc[stats_df["player_id"] == 2546, "plus_minus"].values[0] == 14


def test_toc_calc_player(setup):
    """
    testing time on court calculations
    """

    pbp = setup

    toc = pbp._toc_calc_player()

    assert toc.loc[toc["player_id"] == 1894, "toc"].values[0] == 2307
    assert toc.loc[toc["player_id"] == 947, "toc"].values[0] == 2452
    assert toc.loc[toc["player_id"] == 1894, "toc_string"].values[0] == "38:27"
    assert toc.loc[toc["player_id"] == 947, "toc_string"].values[0] == "40:52"


def test_playerbygamestats(setup):

    pbp = setup

    pbg = pbp.playerbygamestats()

    assert pbg.loc[pbg["player_id"] == 1894, "toc"].values[0] == 2307
    assert pbg.loc[pbg["player_id"] == 947, "toc"].values[0] == 2452
    assert pbg.loc[pbg["player_id"] == 1894, "toc_string"].values[0] == "38:27"
    assert pbg.loc[pbg["player_id"] == 947, "toc_string"].values[0] == "40:52"
    assert pbg.loc[pbg["player_id"] == 1894, "plus_minus"].values[0] == -8
    assert pbg.loc[pbg["player_id"] == 947, "plus_minus"].values[0] == 16
    assert pbg.loc[pbg["player_id"] == 948, "plus_minus"].values[0] == 18
    assert pbg.loc[pbg["player_id"] == 2549, "plus_minus"].values[0] == -9
    assert pbg.loc[pbg["player_id"] == 2059, "plus_minus"].values[0] == 6
    assert pbg.loc[pbg["player_id"] == 1510, "plus_minus"].values[0] == -12
    assert pbg.loc[pbg["player_id"] == 2546, "plus_minus"].values[0] == 14
    assert pbg.loc[pbg["player_id"] == 1894, "pf"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 947, "pf"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 948, "pf"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 2549, "pf"].values[0] == 5
    assert pbg.loc[pbg["player_id"] == 2059, "pf"].values[0] == 5
    assert pbg.loc[pbg["player_id"] == 1510, "pf"].values[0] == 5
    assert pbg.loc[pbg["player_id"] == 2546, "pf"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 1894, "tov"].values[0] == 6
    assert pbg.loc[pbg["player_id"] == 947, "tov"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 948, "tov"].values[0] == 1
    assert pbg.loc[pbg["player_id"] == 2549, "tov"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 2059, "tov"].values[0] == 3
    assert pbg.loc[pbg["player_id"] == 1510, "tov"].values[0] == 1
    assert pbg.loc[pbg["player_id"] == 2546, "tov"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 1894, "stl"].values[0] == 2
    assert pbg.loc[pbg["player_id"] == 947, "stl"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 948, "stl"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 2549, "stl"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 2059, "stl"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 1510, "stl"].values[0] == 2
    assert pbg.loc[pbg["player_id"] == 2546, "stl"].values[0] == 3
    assert pbg.loc[pbg["player_id"] == 1894, "dreb"].values[0] == 2
    assert pbg.loc[pbg["player_id"] == 947, "dreb"].values[0] == 3
    assert pbg.loc[pbg["player_id"] == 948, "dreb"].values[0] == 8
    assert pbg.loc[pbg["player_id"] == 2549, "dreb"].values[0] == 6
    assert pbg.loc[pbg["player_id"] == 2059, "dreb"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 1894, "oreb"].values[0] == 2
    assert pbg.loc[pbg["player_id"] == 947, "oreb"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 948, "oreb"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 2549, "oreb"].values[0] == 3
    assert pbg.loc[pbg["player_id"] == 2059, "oreb"].values[0] == 2
    assert pbg.loc[pbg["player_id"] == 1894, "ast"].values[0] == 5
    assert pbg.loc[pbg["player_id"] == 947, "ast"].values[0] == 7
    assert pbg.loc[pbg["player_id"] == 948, "ast"].values[0] == 3
    assert pbg.loc[pbg["player_id"] == 2549, "ast"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 2059, "ast"].values[0] == 3
    assert pbg.loc[pbg["player_id"] == 1894, "blk"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 947, "blk"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 948, "blk"].values[0] == 1
    assert pbg.loc[pbg["player_id"] == 2549, "blk"].values[0] == 3
    assert pbg.loc[pbg["player_id"] == 2059, "blk"].values[0] == 1
    assert pbg.loc[pbg["player_id"] == 1894, "fgm"].values[0] == 10
    assert pbg.loc[pbg["player_id"] == 1894, "fga"].values[0] == 20
    assert pbg.loc[pbg["player_id"] == 1894, "tpm"].values[0] == 1
    assert pbg.loc[pbg["player_id"] == 1894, "tpa"].values[0] == 2
    assert pbg.loc[pbg["player_id"] == 1894, "ftm"].values[0] == 5
    assert pbg.loc[pbg["player_id"] == 1894, "fta"].values[0] == 6
    assert pbg.loc[pbg["player_id"] == 947, "fgm"].values[0] == 11
    assert pbg.loc[pbg["player_id"] == 947, "fga"].values[0] == 26
    assert pbg.loc[pbg["player_id"] == 947, "tpm"].values[0] == 0
    assert pbg.loc[pbg["player_id"] == 947, "tpa"].values[0] == 2
    assert pbg.loc[pbg["player_id"] == 947, "ftm"].values[0] == 4
    assert pbg.loc[pbg["player_id"] == 947, "fta"].values[0] == 6


def test_calc_poss_player(setup):
    """
    test to make sure possession calculation is working hard to test without
    manually counting and this is close enough
    """

    pbp = setup
    poss = pbp._poss_calc_player()
    assert isinstance(poss, pd.DataFrame)


def test_calc_poss_team(setup):
    """
    test to make sure possession calculation is working hard to test without
    manually counting and this is close enough
    """

    pbp = setup
    poss = pbp._poss_calc_team()

    assert isinstance(poss, pd.DataFrame)


def test_calc_point_team(setup):
    """
    test to make sure team totals for field goals, free throws and three points
    are accurate
    """

    pbp = setup
    points = pbp._point_calc_team()

    assert points.loc[points["team_id"] == 1610612743, "fgm"].values[0] == 46
    assert points.loc[points["team_id"] == 1610612743, "fga"].values[0] == 85
    assert points.loc[points["team_id"] == 1610612743, "tpm"].values[0] == 10
    assert points.loc[points["team_id"] == 1610612743, "tpa"].values[0] == 20
    assert points.loc[points["team_id"] == 1610612743, "ftm"].values[0] == 21
    assert points.loc[points["team_id"] == 1610612743, "fta"].values[0] == 32
    assert points.loc[points["team_id"] == 1610612743, "points_for"].values[0] == 123
    assert points.loc[points["team_id"] == 1610612746, "fgm"].values[0] == 37
    assert points.loc[points["team_id"] == 1610612746, "fga"].values[0] == 79
    assert points.loc[points["team_id"] == 1610612746, "tpm"].values[0] == 7
    assert points.loc[points["team_id"] == 1610612746, "tpa"].values[0] == 14
    assert points.loc[points["team_id"] == 1610612746, "ftm"].values[0] == 26
    assert points.loc[points["team_id"] == 1610612746, "fta"].values[0] == 29
    assert points.loc[points["team_id"] == 1610612746, "points_for"].values[0] == 107


def test_calc_assist_team(setup):
    """
    test to make sure team assist calculation is working properly
    """

    pbp = setup
    assist = pbp._assist_calc_team()

    assert assist.loc[assist["team_id"] == 1610612746, "ast"].values[0] == 21
    assert assist.loc[assist["team_id"] == 1610612743, "ast"].values[0] == 31


def test_calc_rebound_team(setup):
    """
    test to make sure team rebound calculations are working
    """
    pbp = setup
    rebound = pbp._rebound_calc_team()

    assert rebound.loc[rebound["team_id"] == 1610612746, "oreb"].values[0] == 6
    assert rebound.loc[rebound["team_id"] == 1610612743, "oreb"].values[0] == 9
    assert rebound.loc[rebound["team_id"] == 1610612746, "dreb"].values[0] == 32
    assert rebound.loc[rebound["team_id"] == 1610612743, "dreb"].values[0] == 30
