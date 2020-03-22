class PbP:
    '''
    This class represents one game of of an NBA play by play dataframe. I am
    building methods on top of this class to streamline the calculation of
    stats from the play by player and then insertion into a database of the
    users choosing
    '''
    def __init__(self, pbp_df):
        self.df = pbp_df
