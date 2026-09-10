import pandas as pd

def melt_player_stats(original_df):

    game_info = ['match_id','game_id', 'datetime', 'team_player']
    player_info = ['id', 'kills', 'deaths', 'assists', 'adr', 'kast', 'kddiff']

    long_df = pd.melt(original_df, 
                            id_vars = game_info[:3], 
                            value_vars= [f"team{x}_player{y}_{z}" for x in range(1,3) for y in range(1,6) for z in player_info], 
                            value_name= 'stats')
    long_df[['team_player', 'stats_var']] = long_df['variable'].str.rsplit("_", n = 1, expand = True)

    long_df = (long_df.pivot_table(values = 'stats', 
                                          index= ['match_id', 'game_id', 'datetime', 'team_player'], 
                                          columns= 'stats_var')
                        .reset_index())
    long_df = long_df[game_info + player_info]

    long_df['datetime'] = pd.to_datetime(long_df['datetime'])
    long_df['key'] = (long_df['game_id'].astype(str)+ ' ' + long_df['id'].astype(str))

    return long_df

def remove_duplicated_players(long_df):
    n_begin = len(long_df)

    long_df.drop_duplicates(subset = 'key'
                                      , keep = False
                                      , inplace = True
                                      , ignore_index = True)

    n_rows_removed = n_begin - len(long_df)
    print(f"Removed {n_rows_removed} rows. {len(long_df)} rows remain")

    return long_df

def hist_player_avg(long_df):

    long_df = long_df.sort_values(['datetime', 'game_id', 'team_player'], ascending= [True, True, True]).reset_index(level = 0, drop=True)

    stats_list = ['kills','deaths','assists','adr','kast','kddiff']

    hist_stats_columns = [f"{x}_hist_avg" for x in stats_list]

    long_df[hist_stats_columns] = (long_df.groupby('id')[stats_list]
                                                .transform(lambda x: x.expanding().mean().shift(1)))

    global_hist_avg = (long_df[stats_list].expanding()
                                          .mean()
                                          .shift(1))
    global_hist_avg.columns = hist_stats_columns

    long_df[hist_stats_columns] = long_df[hist_stats_columns].fillna(global_hist_avg)

    long_df = long_df.drop(0)

    return long_df

def fill_missing_player_stats(long_df):
    stats_list = ['kills','deaths','assists','adr','kast','kddiff']
    
    for stat in stats_list:
        long_df[stat] = long_df[stat].fillna(long_df[f'{stat}_hist_avg'])

    return long_df

def pivot_player_stats(long_df):
    player_info = ['id', 'kills', 'deaths', 'assists', 'adr', 'kast', 'kddiff']
    
    long_df = (long_df.pivot(values = player_info, 
                                    index= ['match_id', 'game_id', 'datetime'], 
                                    columns= 'team_player'))
    
    reshaping_columns_names = [f"{team_player}_{stat}" for stat, team_player in long_df.columns]
    long_df.columns = reshaping_columns_names
    wide_stats_df = long_df.reset_index()

    return wide_stats_df

def remove_incomplete_games(wide_stats_df):
    n_begin = len(wide_stats_df)

    player_info = ['id', 'kills', 'deaths', 'assists', 'adr', 'kast', 'kddiff']
    player_info_columns = [f"team{x}_player{y}_{z}" for x in range(1,3) for y in range(1,6) for z in player_info]

    wide_stats_df = wide_stats_df.dropna(subset = player_info_columns)

    n_rows_removed = n_begin - len(wide_stats_df)
    print(f"Removed {n_rows_removed} rows. {len(wide_stats_df)} rows remain")

    return wide_stats_df

def merge_player_stats(original_df, wide_stats_df):

    original_df = pd.merge(original_df, wide_stats_df
                          , on='game_id'
                          , how='left'
                          , suffixes = ('', '_right'))

    player_info = ['id', 'kills', 'deaths', 'assists', 'adr', 'kast', 'kddiff']
    stats_columns = [f"team{x}_player{y}_{z}" for x in range(1,3) for y in range(1,6) for z in player_info]

    for column in stats_columns:
        original_df[column] = original_df[column].fillna(original_df[f'{column}_right'])

    original_df = original_df.drop(columns=[f'{col}_right' for col in stats_columns])
    original_df = original_df.drop(columns=['match_id_right' , 'datetime_right'])
    
    return original_df
 
def add_player_historical_stats(original_df):

    long_df = melt_player_stats(original_df)
    long_df = remove_duplicated_players(long_df)
    long_df = hist_player_avg(long_df)
    long_df = fill_missing_player_stats(long_df)

    wide_stats_df = pivot_player_stats(long_df)
    wide_stats_df = remove_incomplete_games(wide_stats_df)

    enriched_df = merge_player_stats(original_df, wide_stats_df)
    enriched_df = remove_incomplete_games(enriched_df)

    return enriched_df