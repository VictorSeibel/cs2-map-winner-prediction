import pandas as pd


def wide_to_long_team(wide_df):
    game_info = ["match_id", "game_id", "datetime", "team1", "team2"]
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

    long_df[["team", "player", "stats_var"]] = long_df["variable"].str.rsplit(
        "_", n=2, expand=True
    )

    long_df["team_name"] = long_df.apply(
        lambda row: row[row["team"]],
        axis=1
    )

    long_df = long_df.pivot_table(
        values="stats",
        index=["match_id", "game_id", "datetime", "team", "team_name", "player"],
        columns="stats_var",
    ).reset_index()
    
    return long_df