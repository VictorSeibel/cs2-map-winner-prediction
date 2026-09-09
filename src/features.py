import pandas as pd
import numpy as np

def melt_stats(interim_df):

    game_info = ['match_id','game_id', 'datetime', 'team', 'player']
    player_info = ['id', 'kills', 'deaths', 'assists', 'adr', 'kast', 'kddiff']

    long_df = pd.melt(interim_df, 
                            id_vars = game_info[:3], 
                            value_vars= [f"team{x}_player{y}_{z}" for x in range(1,3) for y in range(1,6) for z in player_info], 
                            value_name= 'stats')
    long_df[['team', 'player', 'stats_var']] = long_df['variable'].str.split("_", expand = True)

    long_df = (long_df.pivot_table(values = 'stats', 
                                          index= ['match_id', 'game_id', 'datetime', 'team', 'player'], 
                                          columns= 'stats_var')
                        .reset_index())
    long_df = long_df[game_info + player_info]
    long_df['datetime'] = pd.to_datetime(long_df['datetime'])
    
    return long_df
    
def hist_player_avg(long_df):
    long_df = long_df.sort_values(['datetime', 'game_id', 'team', 'player'], ascending= [True, True, True, True]).reset_index(level = 0, drop=True)

    stats_list = ['kills','deaths','assists','adr','kast','kddiff']

    hist_stats_columns = [f"{x}_hist_avg" for x in stats_list]

    long_df[hist_stats_columns] = (long_df.groupby('id')[stats_list]
                                                .transform(lambda x: x.expanding().mean().shift(1)))

    global_hist_avg = long_df[stats_list].expanding().mean().shift(1)
    global_hist_avg.columns = hist_stats_columns

    long_df[hist_stats_columns] = long_df[hist_stats_columns].fillna(global_hist_avg)

    long_df = long_df.drop(0)

    return long_df