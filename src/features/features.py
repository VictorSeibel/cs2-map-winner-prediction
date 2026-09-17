def aggregate_team_stats(processed_df):

    all_df_columns = processed_df.columns.to_list()
    stats_list = ["adr", "assists", "kast", "kddiff"]
    group_cols = ["game_id", "team", "team_name", "datetime"]
    remaining_cols = [
        x
        for x in all_df_columns
        if x
        not in (stats_list + group_cols + ["team1_id", "team1", "team2_id", "team2"])
    ]

    agg_dict = {y: "mean" for y in stats_list} | {z: "first" for z in remaining_cols}

    team_df = processed_df.groupby(group_cols).agg(agg_dict).reset_index()

    team_df.rename(columns={x: f"team_avg_{x}" for x in stats_list}, inplace=True)

    return team_df


def hist_team_avg(team_df):

    stats_list = ["adr", "assists", "kast", "kddiff"]

    team_avg_stats = [f"team_avg_{x}" for x in stats_list]

    hist_team_avg_stats = [f"hist_team_avg_{y}" for y in stats_list]

    team_df = team_df.sort_values(
        ["datetime", "game_id", "team"], ascending=[True, True, True]
    ).reset_index(drop=True)

    team_df[hist_team_avg_stats] = team_df.groupby(["team_name"])[
        team_avg_stats
    ].transform(lambda x: x.rolling(10, min_periods=1).mean().shift(1))

    global_hist_avg_team_status = team_df[team_avg_stats].expanding().mean().shift(1)
    global_hist_avg_team_status.columns = hist_team_avg_stats

    team_df[hist_team_avg_stats] = team_df[hist_team_avg_stats].fillna(
        global_hist_avg_team_status
    )

    return team_df


def remove_incomplete_teams(team_df):

    stats_list = ["adr", "assists", "kast", "kddiff"]
    hist_team_avg_stats = [f"hist_team_avg_{y}" for y in stats_list]

    team_df = team_df.dropna(subset=hist_team_avg_stats)

    return team_df


def drop_current_game_stats(team_df):

    stats_list = ["adr", "assists", "kast", "kddiff"]

    team_avg_stats = [f"team_avg_{y}" for y in stats_list]

    team_df = team_df.drop(team_avg_stats, axis=1)

    return team_df


def build_team_features(processed_df):

    team_df = aggregate_team_stats(processed_df)
    team_df = hist_team_avg(team_df)
    team_df = remove_incomplete_teams(team_df)
    team_df = drop_current_game_stats(team_df)

    return team_df
