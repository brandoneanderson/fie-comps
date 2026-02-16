from pathlib import Path
# FIE Comps path
PROJECT_ROOT = Path(__file__).resolve().parent.parent


ML_DIR = PROJECT_ROOT / "ML"
DATASET_DIR = ML_DIR / "datasets"
OLD_DATASET_DIR = DATASET_DIR / "older_datasets"

EXTENSIONS_DIR = PROJECT_ROOT / "parser" / "Extensions"

BENIGN_EXT_CSV = DATASET_DIR / "Benign_ext.csv"
MAL_EXT_CSV = DATASET_DIR / "Malicious_ext.csv"
MAL_CHROME_STATS_CSV = DATASET_DIR / "results_with_versions.csv"

OUTPUT_CSV = DATASET_DIR / "output.csv"

OUTPUTB1_CSV = OLD_DATASET_DIR / "outputB_0_50.csv"
OUTPUTB2_CSV = OLD_DATASET_DIR / "outputB_50_100.csv"
OUTPUTB3_CSV = OLD_DATASET_DIR / "outputB_100_200.csv"
OUTPUTB4_CSV = OLD_DATASET_DIR / "outputB_200_300.csv"
OUTPUTB5_CSV = OLD_DATASET_DIR / "outputB_300_400.csv"
OUTPUTB6_CSV = OLD_DATASET_DIR / "outputB_400_1000.csv"
OUTPUTB7_CSV = OLD_DATASET_DIR / "outputB_1000_rest.csv"

OUTPUTM1_CSV = OLD_DATASET_DIR / "outputM.csv"
OUTPUTM2_CSV = OLD_DATASET_DIR / "outputM50_200.csv"
OUTPUTM3_CSV = OLD_DATASET_DIR / "outputM200_500.csv"
OUTPUTM4_CSV = OLD_DATASET_DIR / "outputM500_700.csv"
OUTPUTM5_CSV = OLD_DATASET_DIR / "outputM700_900.csv"
OUTPUTM6_CSV = OLD_DATASET_DIR / "outputM900_rest.csv"

OUTPUTMCHROME_CSV = OLD_DATASET_DIR / "outputM_allextsChrome.csv"

FINAL_B_CSV = DATASET_DIR / "final_B.csv"
FINAL_M_CSV = DATASET_DIR / "final_M.csv"


SUB_RESULTS_CSV = DATASET_DIR / "SubcriptionResult.csv"

if __name__ == "__main__":
    print(PROJECT_ROOT)