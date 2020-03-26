# `nba_parser`

This will be a repository where I store all my scripts and tests for compiling and calculating
NBA game data from play by play dataframe objects.

The main hook of the `nba_parser` will the the `PbP` class that will take a play
by play Pandas dataframe either as the direct output from my [nba_scraper](https://github.com/mcbarlowe/nba_scraper)
or as a Pandas dataframe created from the csv output of the `nba_scraper` saved
to file.

# Player Stats

Player stats can be calculated from a play by play dataframe with just a few
lines of code.

```python
import nba_scraper.nba_scraper as ns
import nba_parser.nba_parser as npsr

game_df = ns.scrape_game([20700233])
pbp = PbP(game_df)
player_stats = pbp.playerbygamestats()
```

Which produces a dataframe containing the stats of field goals made, field goals attempted,
three points made, three points attempted, free throws made, free throws attempted,
steals, turnovers, blocks, personal fouls, minutes played(toc), offensive rebounds,
and defensive rebounds.
