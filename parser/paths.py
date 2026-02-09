from pathlib import Path
# FIE Comps path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


ML_DIR = PROJECT_ROOT / "ML"
DATASET_DIR = ML_DIR / "datasets"

EXTENSIONS_DIR = PROJECT_ROOT / "parser" / "Extensions"

BENIGN_EXT_CSV = DATASET_DIR / "Benign_ext.csv"
MAL_EXT_CSV = DATASET_DIR / "Malicious_ext.csv"

if __name__ == "__main__":
    print(PROJECT_ROOT)