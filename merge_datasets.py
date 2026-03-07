import pandas as pd
import numpy as np
from pathlib import Path

from parser.paths import *

# BENIGN_CSV = "begign.csv"
# MAL_CSV = "malicoious.csv"

def load_and_label(path: str, label: int) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["label"] = label
    return df

def clean_empty_rows(df):
    exclude_cols = ["label", "Extension Name"]
    feature_cols = [c for c in df.columns if c not in exclude_cols]

    feature_df = df[feature_cols].fillna(0)

    # Count how many non-zero features exist
    non_zero_counts = (feature_df != 0).sum(axis=1)

    print("Rows before:", len(df))
    print("Rows with <= 1 non-zero feature:", (non_zero_counts <= 1).sum())

    # Remove rows with 0 or 1 non-zero feature
    df_cleaned = df[non_zero_counts > 1].copy()

    print("Rows after:", len(df_cleaned))
    print("-" * 40)

    return df_cleaned


df_b = load_and_label(FINAL_B_CSV, 0)
df_m = load_and_label(FINAL_M_CSV, 1)
print(df_b.shape)
df_b = clean_empty_rows(df_b)
df_m = clean_empty_rows(df_m)

##  RANDOMLY CHOOSES 1000 MAL and 300 ben
df_m = df_m.sample(n=3000, random_state=42).reset_index(drop=True)
df_b = df_b.sample(n=2865, random_state=42).reset_index(drop=True)

df_m.to_csv("FINAL2_M.csv", index=False)
df_b.to_csv("FINAL2_B.csv", index=False)

df = pd.concat((df_b, df_m), ignore_index=True)


# do we want to drop non-feature columns
# NON_FEATURE_COLS = ["Extension Name", "label"]
# feature_cols = [c for c in df.columns if c not in NON_FEATURE_COLS]

df.to_csv('training.csv', index=False)

print("combined shape:", df.shape)

