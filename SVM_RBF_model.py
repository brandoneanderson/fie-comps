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

# K-best features from RF output
# OLD_K_BEST_FEATURES = [
#     "specific_characters", "avg_line_length", "dynamic_code_gen_functions",
#     "event_handlers", "DOM_operations", "keyword_density", "whitespace %",
#     "DOM_change_sinks_density", "string_entropy", "word_size",
#     "webRequestBlocking", "DOM_operations_density", "event_handlers_density",
#     "XMLHttpRequests_density", "num_external_urls", "DOM_change_sinks",
#     "num_script_src_attrs", "num_script_tags", "num_background_image",
#     "storage", "All https domains", "XMLHttpRequests", "num_import_rules",
#     "tabs", "modification_callbacks_density", "webRequest", "security_policy",
#     "cookies", "num_iframe_tags", "num_http_urls", "modification_callbacks",
#     "management", "num_form_tags", "num_meta_refresh",
#     "num_external_iframe_src", "num_behavior", "notifications",
# ]

K_BEST_FEATURES = ['avg_line_length', 'specific_characters', 'dynamic_code_gen_functions',
       'event_handlers', 'DOM_operations', 'keyword_density', 'whitespace %',
       'DOM_change_sinks_density', 'string_entropy', 'word_size',
       'DOM_operations_density', 'webRequestBlocking',
       'event_handlers_density', 'num_external_urls', 'DOM_change_sinks',
       'XMLHttpRequests_density', 'num_script_tags', 'num_script_src_attrs',
       'num_background_image', 'storage', 'All https domains',
       'XMLHttpRequests', 'tabs', 'webRequest',
       'modification_callbacks_density', 'num_import_rules', 'security_policy',
       'num_iframe_tags', 'num_form_tags', 'cookies',
       'num_external_iframe_src', 'notifications', 'num_http_urls',
       'modification_callbacks', 'num_meta_refresh', 'num_behavior']

def pick_threshold_max_f1(y_true, proba):
    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    f1 = (2 * precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-12)
    i = int(np.argmax(f1))
    return float(thresholds[i])

def pick_threshold_youden(y_true, proba):
    fpr, tpr, thr = roc_curve(y_true, proba)
    i = int(np.argmax(tpr - fpr))
    return float(thr[i])


if __name__ == "__main__":
    # TRAINING_CSV = "/Users/ishapatel/COMPS/fie-comps/ML/datasets/training.csv"
    # MODEL_BUNDLE_PATH = "/Users/ishapatel/COMPS/fie-comps/ML/models/svm_rbf_bundle.joblib"

    TRAINING_CSV = str(TRAINING_CSV)
    MODEL_BUNDLE_PATH = str(SVM_BUNDLE_PATH)

    #Load in dataframe
    df = pd.read_csv(TRAINING_CSV)

    # Split dataset into features and labels
    y = df["label"].astype(int)

    # Checking each column feature, cvs is nasty
    #print(ext_dataset_csv_df.columns)

    X = df[K_BEST_FEATURES].apply(pd.to_numeric, errors="coerce").fillna(0.0)

    # Split dataset into X_train, y_train, X_test, Y_test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)

    # See if shapes match expected output
    print('Training data shape: ', X_train.shape)
    print('Training labels shape: ', y_train.shape)
    print('Test data shape: ', X_test.shape)
    print('Test labels shape: ', y_test.shape)

    # Pipeline: scale then SVM-RBF
    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("svm", SVC(kernel="rbf", probability=True, class_weight = "balanced", random_state=42))
    ])

    # Hyperparameter tuning
    param_grid = {
        # "svm__C": [0.1, 1, 10, 100, 1000],
        "svm__C": [3, 4, 5, 6, 7, 8, 9, 10],
        # "svm__gamma": [1e-4, 1e-3, 1e-2, 1e-1, "scale"],
        "svm__gamma":[0.02, 0.03, 0.04, 0.05, 0.06],
        "svm__class_weight": [
            None,
            "balanced",
            {0:1, 1:1.5},
            {0:1, 1:2},
            {0:1, 1:3},
            {0:1, 1:4},
        ]
    }

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    gs = GridSearchCV(
        pipe,
        param_grid=param_grid,
        # scoring="f1",
        scoring="average_precision",
        cv=cv,
        n_jobs=-1,
        verbose=2
    )

    gs.fit(X_train, y_train)
    best_model = gs.best_estimator_
    print("Best params:", gs.best_params_)
    print("Best CV F1:", gs.best_score_)
    # print("Best CV score (average_precision):", gs.best_score_)


    # Evaluate on test
    cal = CalibratedClassifierCV(best_model, method="sigmoid", cv=5)
    cal.fit(X_train, y_train)
    proba = cal.predict_proba(X_test)[:, 1]
    # proba = best_model.predict_proba(X_test)[:, 1]

     # baseline @ 0.5
    pred_05 = (proba >= 0.5).astype(int)
    print("\n=== Test @ threshold 0.5 ===")
    print("ROC-AUC:", roc_auc_score(y_test, proba))
    print("PR-AUC:", average_precision_score(y_test, proba))
    print("Confusion matrix:\n", confusion_matrix(y_test, pred_05))
    print(classification_report(y_test, pred_05, digits=3))

    # 7) Choose best threshold by max F1 (optional but good)
    precision, recall, thresholds = precision_recall_curve(y_test, proba)
    f1_scores = (2 * precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-12)
    best_i = int(np.argmax(f1_scores))
    best_thresh = float(thresholds[best_i])

    pred_best = (proba >= best_thresh).astype(int)
    print("\n=== Test @ threshold chosen by max F1 ===")
    print("Chosen threshold:", best_thresh)
    print("Confusion matrix:\n", confusion_matrix(y_test, pred_best))
    print(classification_report(y_test, pred_best, digits=3))

    # 8) Save model bundle
    bundle = {
        # "model": best_model,
        "model": cal,
        "feature_cols": K_BEST_FEATURES,
        "threshold": best_thresh,
        "best_params": gs.best_params_,
    }

    Path(MODEL_BUNDLE_PATH).parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, MODEL_BUNDLE_PATH)  # set this in paths.py
    print(f"Saved model bundle to: {MODEL_BUNDLE_PATH}")


    #ROC curve
    fpr, tpr, thr = roc_curve(y_test, proba)
    youden = tpr - fpr
    thr_youden = float(thr[np.argmax(youden)])

    pred_youden = (proba >= thr_youden).astype(int)
    print("\n=== Test @ threshold chosen by Youden J (TPR-FPR) ===")
    print("Chosen threshold:", thr_youden)
    print("Confusion matrix:\n", confusion_matrix(y_test, pred_youden))
    print(classification_report(y_test, pred_youden, digits=3))


   