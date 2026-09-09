import pandas as pd
import numpy as np
from pathlib import Path
import kaggle

def download_data(dataset_slug = "cs2_all_tiers_games.csv", dest_dir = "data/raw"):
    # dataset_slug receives the kaggle url
    dest_path = Path(dest_dir)

    if dest_path.exists() and any(dest_path.iterdir()):
        print(f"Dataframes already exists in {dest_dir}.")
        return

    dest_path.mkdir(parents=True, exist_ok=True)
    kaggle.api.dataset_download_files(dataset_slug, path=dest_dir, unzip=True)
    print(f"DataFrame downloaded successfully. extracted at {dest_dir}")

def load_dataframe(file: str):
    df = pd.read_csv(f"../data/raw/{file}")
    print(f"DataFrame successfully loaded. There's {df.shape}")

    return df

def remove_summary_serie(interim_df):
    # remove "is_total" == True, returning the total of rows removed
    n_begin = len(interim_df)

    interim_df = interim_df[interim_df['is_total'] != True]

    n_rows_removed = n_begin - len(interim_df)
    print(f"Removed {n_rows_removed} rows. {len(interim_df)} rows remain")
    return interim_df

def remove_invalid_bestof(interim_df):
    # remove where 'bestOf' is invalid. Examples: BO3 -> score1_match: 3 and score2_match: 0 ; score1_match: 2 and score2_match: 2; score1_match: 1 and score2_match: 0

    n_begin = len(interim_df)
    limit = (interim_df['bestOf'] // 2) + 1
    max_score = interim_df[['score1_match', 'score2_match']].max(axis=1)
    min_score = interim_df[['score1_match', 'score2_match']].min(axis=1)

    valid_rows = (max_score == limit) & (min_score < limit)
    interim_df = interim_df[valid_rows]

    n_removed = n_begin - len(interim_df)
    print(f"Removed {n_removed} rows. {len(interim_df)} rows remain")
    return interim_df

def remove_missing_player_id(interim_df):
    n_begin = len(interim_df)
    null_id = interim_df[[f"team{x}_player{y}_id" for x in range(1,3) for y in range(1,6)]].isnull()
    rows_with_missing_id = null_id.any(axis=1)

    interim_df = interim_df[~ rows_with_missing_id]

    n_rows_removed = n_begin - len(interim_df)
    print(f"Removed {n_rows_removed} rows. {len(interim_df)} rows remain")
    return interim_df

def remove_missing_maps_id(interim_df):

    n_begin = len(interim_df)

    null_map_id = interim_df['map_id'].isnull()

    interim_df = interim_df[~ null_map_id]

    n_rows_removed = n_begin - len(interim_df)
    print(f"Removed {n_rows_removed} rows. {len(interim_df)} rows remain")
    return interim_df