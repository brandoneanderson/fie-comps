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

df_b = load_and_label(FINAL_B_CSV, 0)
df_m = load_and_label(FINAL_M_CSV, 1)

##  RANDOMLY CHOOSES 1000 MAL and 300 ben
df_m = df_m.sample(n=1000, random_state=42).reset_index(drop=True)
df_b = df_b.sample(n=3000, random_state=42).reset_index(drop=True)

df = pd.concat((df_b, df_m), ignore_index=True)


# do we want to drop non-feature columns
# NON_FEATURE_COLS = ["Extension Name", "label"]
# feature_cols = [c for c in df.columns if c not in NON_FEATURE_COLS]

df.to_csv('training_csv', index=False)

print("combined shape:", df.shape)

