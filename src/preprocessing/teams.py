import pandas as pd


def wide_to_long_team(wide_df):
    game_info = [wide_df.columns[x] for x in range(17)]
    player_info = ["id", "assists", "adr", "kast", "kddiff"]

    long_df = pd.melt(
        wide_df,
        id_vars=game_info,
        value_vars=[
            f"team{x}_player{y}_{z}"
            for x in range(1, 3)
            for y in range(1, 6)
            for z in player_info
        ],
        value_name="stats",
    )

    stats_info_splitted = ["team", "player", "stats_var"]

    long_df[stats_info_splitted] = long_df["variable"].str.rsplit("_", n=2, expand=True)

    long_df["team_name"] = long_df.apply(lambda row: row[row["team"]], axis=1)

    long_df = long_df.pivot_table(
        values="stats",
        index=game_info + stats_info_splitted[:2] + ["team_name"],
        columns="stats_var",
    ).reset_index()

    long_df = long_df.drop(columns= ['player', 'id'])
    
    return long_df
