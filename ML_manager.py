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
    return model, feature_cols, threshold, bundle

def predict_from_feature_dict(feat: dict, model, feature_cols, threshold):
    X = pd.DataFrame([feat])

    # align columns
    for c in feature_cols:
        if c not in X.columns:
            X[c] = 0.0

    X = X[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)

    prob = float(model.predict_proba(X)[0, 1])
    score = risk_score_thresholded(prob, threshold)
    level = risk_level(score)

    return {
        "label": "MALICIOUS" if prob >= threshold else "BENIGN",
        "prob_malicious": prob,
        "risk_score": score,
        "risk_level": level,
        "confidence": confidence_from_margin(prob, threshold),
        "threshold": float(threshold),
        "action": recommended_action(level),
    }
def batch_score_csv(csv_path, model, feature_cols, threshold):
    df = pd.read_csv(csv_path)

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

if __name__ == "__main__":
    model, feature_cols, threshold, bundle = load_svm_bundle(SVM_BUNDLE_PATH)

    print("Loaded bundle:", SVM_BUNDLE_PATH)
    print("Threshold:", threshold)
    print("Num features:", len(feature_cols))

    # batch test on benign CSV by default
    batch_score_csv(FINAL_B_CSV, model, feature_cols, threshold)

    # # Load the bundled pipeline
    # model_bundle = joblib.load(SVM_BUNDLE_PATH)
    # # print(model_bundle)

    # model = model_bundle["model"]
    # feature_cols = model_bundle["feature_cols"]
    # threshold = model_bundle["threshold"]
    # # Predict classes
    # # svm_rb = SVC(kernel = 'rbf', C = 10, class_weight='balanced', gamma=0.01, random_state=42)
    # # X = df[K_BEST_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0.0)

    # predict_new_df = pd.read_csv(FINAL_B_CSV)

    # X_new = (
    #     predict_new_df[feature_cols]
    #     .apply(pd.to_numeric, errors="coerce")
    #     .fillna(0.0)
    # )

    # proba = model.predict_proba(X_new) [:, 1]


    # predictions = (proba >= threshold).astype(int)

    
    # print(predictions)
    # print(len(predictions))
    # pos = 0
    # neg = 0
    # for pred in predictions:
    #     if pred ==1:
    #         pos += 1
    #     else:
    #         neg += 1

    
    # print("flagged_malicious_rate", pos/len(predictions))
    # print("flagged_benign_rate", neg/len(predictions))
    # print("mean_prob_malicious", float(np.mean(proba)))
    # print("median_prob_malicious", float(np.median(proba)))

    # scores = [risk_score_thresholded(p, threshold) for p in proba]
    # levels = [risk_level(s) for s in scores]

    # print("avg_risk_score", float(np.mean(scores)))
    # print("risk_level_counts", pd.Series(levels).value_counts().to_dict())
# Optional: Get probability scores
# probabilities = model_bundle.predict_proba(new_data)


