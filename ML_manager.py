from paths import *
import pandas as pd
import numpy as np
import joblib

from ML.scoring import *


def load_svm_bundle(bundle_path):
    bundle = joblib.load(bundle_path)
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    threshold = float(bundle["threshold"])
    return model, feature_cols, threshold

# def predict_from_feature_dict(feat: dict, model, feature_cols, threshold):
#     X = pd.DataFrame([feat])

#     # align columns
#     for c in feature_cols:
#         if c not in X.columns:
#             X[c] = 0.0

#     X = X[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)

#     prob = float(model.predict_proba(X)[0, 1])
#     score = risk_score_thresholded(prob, threshold)
#     level = risk_level(score)

#     return {
#         "label": "MALICIOUS" if prob >= threshold else "BENIGN",
#         "prob_malicious": prob,
#         "risk_score": score,
#         "risk_level": level,
#         "confidence": confidence_from_margin(prob, threshold),
#         "threshold": float(threshold),
#         "action": recommended_action(level),
#     }

def batch_score_csv(df, model, feature_cols, threshold):

    X = (
        df[feature_cols]
        .apply(pd.to_numeric, errors="coerce")
        .fillna(0.0)
    )

    proba = model.predict_proba(X)[:, 1]
    preds = (proba >= threshold).astype(int)

    pos = int(np.sum(preds == 1))
    neg = int(np.sum(preds == 0))

    print("rows:", len(df))
    print("flagged_malicious_rate:", pos / len(df))
    print("flagged_benign_rate:", neg / len(df))
    print("mean_prob_malicious:", float(np.mean(proba)))
    print("median_prob_malicious:", float(np.median(proba)))

    scores = [risk_score_thresholded(p, threshold) for p in proba]
    levels = [risk_level(s) for s in scores]
    print("avg_risk_score:", float(np.mean(scores)))
    print("risk_level_counts:", pd.Series(levels).value_counts().to_dict())

def query_model(df):
    model, feature_cols, threshold = load_svm_bundle(SVM_BUNDLE_PATH)

    print("Loaded bundle:", SVM_BUNDLE_PATH)
    print("Threshold:", threshold)
    print("Num features:", len(feature_cols))

    # batch test on benign CSV by default
    batch_score_csv(df, model, feature_cols, threshold)


