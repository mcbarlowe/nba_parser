from nba_parser.nba_parser import PbP
import pandas as pd
import pytest


@pytest.fixture
def setup():
    """
    function for test setup and teardown
    """
    pbp_df = pd.read_csv("test/20700233.csv")
    yield pbp_df


def test_class_build(setup):
    """
    This test makes sure the proper class is instantiated when called
    """
    setup_df = setup
    pbp = PbP(setup_df)

    assert isinstance(pbp, PbP)
    assert isinstance(pbp.df, pd.DataFrame)
