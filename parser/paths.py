from pathlib import Path
# FIE Comps path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


ML_DIR = PROJECT_ROOT / "ML"
DATASET_DIR = ML_DIR / "datasets"

EXTENSIONS_DIR = PROJECT_ROOT / "parser" / "Extensions"

BENIGN_EXT_CSV = DATASET_DIR / "Benign_ext.csv"
MAL_EXT_CSV = DATASET_DIR / "Malicious_ext.csv"

OUTPUT_CSV = DATASET_DIR / "output.cvs"
OUTPUTB_CSV = DATASET_DIR / "outputB.cvs"
OUTPUTM_CSV = DATASET_DIR / "outputM.cvs"
OUTPUTM50_CSV = DATASET_DIR / "outputM50_200.cvs"
OUTPUTM200_CSV = DATASET_DIR / "outputM200_500.cvs"
OUTPUTM700_CSV = DATASET_DIR / "outputM500_700.cvs"
OUTPUTM900_CSV = DATASET_DIR / "outputM700_900.cvs"
OUTPUTM1000_CSV = DATASET_DIR / "outputM700_900.cvs"

SUB_RESULTS_CSV = DATASET_DIR / "SubcriptionResult.cvs"

if __name__ == "__main__":
    print(PROJECT_ROOT)