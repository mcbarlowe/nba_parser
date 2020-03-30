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
import nba_parser as npar

game_df = ns.scrape_game([20700233])
pbp = npar.PbP(game_df)
player_stats = pbp.playerbygamestats()

#can also derive single possessions for RAPM calculations

rapm_shifts = pbp.rapm_possessions()
```

Which produces a dataframe containing the stats of field goals made, field goals attempted,
three points made, three points attempted, free throws made, free throws attempted,
steals, turnovers, blocks, personal fouls, minutes played(toc), offensive rebounds, possessions
and defensive rebounds.

# Team Stats

Team stats are called very similar to player stats.

```python
import nba_scraper.nba_scraper as ns
import nba_parser as npar

game_df = ns.scrape_game([20700233])
pbp = npar.PbP(game_df)
team_stats = pbp.teambygamestats()
```

The team stats that will be calculation are field goals made, field goals attempted,
three points made, three points attempted, free throws made, free throws attempted,
steals, turnovers, blocks, personal fouls, minutes played(toc), offensive rebounds, possessions,
home team, winning team, fouls drawn, shots blocked, total points for, total points against,
and defensive rebounds.

# Team Totals

I've grouped together other stat calculations that work better with larger sample sizes.
This class takes a list of outputs from PbP.teambygamestats() but really it could take a
list of dataframes that are the same structure as that method output. Here's an example
of how it could work in conjunction with `nba_scraper`. I suggest writing the pbp returns to file and then importing them as the `nba_scraper` could time out due to the NBA api timing out from being hit too many times.


```python
import nba_scraper.nba_scraper as ns
import nba_parser as npar

tbg_dfs = []
for game_id in range(20700001, 20700010):
    game_df = ns.scrape_game([game_id])
    pbp = np.PbP(game_df)
    team_stats = pbp.teambygamestats()
    tbg_dfs.append(team_stats)

team_totals = npar.TeamTotals(tbg_dfs)

#produce a dataframe of eFG%, TS%, TOV%, OREB%, FT/FGA, Opponent eFG%,
#Opponent TOV%, DREB%, Opponent FT/FGA, along with summing the other
#stats produced by the teambygamestats() method to allow further
#calculations

team_adv_stats = team_totals.team_advanced_stats()


#to calculate a RAPM regression for teams use this method

team_rapm_df = team_totals.team_rapm_results()
```

# Player Totals

Like with TeamTotals i've grouped player stat calculations that work better
with a larger sample size into its own class. A lot of the hooks are similar
except for the RAPM calculation which is a static method due to the time
to calculate player RAPM shifts is much longer than team shifts so its
best to have them precalculated before attempting a RAPM regression to reduce time.


```python
import nba_scraper.nba_scraper as ns
import nba_parser as npar

pbg_dfs = []
pbp_objects = []
for game_id in range(20700001, 2070010):
    game_df = ns.scrape_game([game_id])
    pbp = np.PbP(game_df)
    pbp_objects.append(pbp)
    player_stats = pbp.playerbygamestats()
    pbg_dfs.append(player_stats)

player_totals = npar.PlayerTotals(pbg_dfs)

#produce a dataframe of eFG%, TS%, TOV%, OREB%, AST%, DREB%,
#STL%, BLK%, USG%, along with summing the other
#stats produced by the playerbygamestats() method to allow further
#calculations

player_adv_stats = player_totals.player_advanced_stats()


#to calculate a RAPM regression for players first have to calculate
#RAPM possessions from the list of PbP objects we collected above

rapm_possession = pd.concat([x.rapm_possessions() for x in pbp_objects])

player_rapm_df = npar.PlayerTotals.player_rapm_results(rapm_possession)
```
