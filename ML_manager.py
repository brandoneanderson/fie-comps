from pathlib import Path
from paths import *
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, learning_curve
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, average_precision_score,
    precision_recall_curve, roc_curve
)

from sklearn.metrics import roc_curve


if __name__ == "__main__":

    # Load the bundled pipeline
    model_bundle = joblib.load(SVM_BUNDLE_PATH)
    # print(model_bundle)

    model = model_bundle["model"]
    feature_cols = model_bundle["feature_cols"]
    threshold = model_bundle["threshold"]
    # Predict classes
    # svm_rb = SVC(kernel = 'rbf', C = 10, class_weight='balanced', gamma=0.01, random_state=42)
    # X = df[K_BEST_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0.0)

    predict_new_df = pd.read_csv(FINAL_B_CSV)

    X_new = (
        predict_new_df[feature_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0.0)
    )

    proba = model.predict_proba(X_new) [:, 1]


    predictions = (proba >= threshold).astype(int)

    
    print(predictions)
    print(len(predictions))
    pos = 0
    neg = 0
    for pred in predictions:
        if pred ==1:
            pos += 1
        else:
            neg += 1

    print("acc", pos/len(predictions))

# Optional: Get probability scores
# probabilities = model_bundle.predict_proba(new_data)
