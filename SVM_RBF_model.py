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
K_BEST_FEATURES = [
    "specific_characters", "avg_line_length", "dynamic_code_gen_functions",
    "event_handlers", "DOM_operations", "keyword_density", "whitespace %",
    "DOM_change_sinks_density", "string_entropy", "word_size",
    "webRequestBlocking", "DOM_operations_density", "event_handlers_density",
    "XMLHttpRequests_density", "num_external_urls", "DOM_change_sinks",
    "num_script_src_attrs", "num_script_tags", "num_background_image",
    "storage", "All https domains", "XMLHttpRequests", "num_import_rules",
    "tabs", "modification_callbacks_density", "webRequest", "security_policy",
    "cookies", "num_iframe_tags", "num_http_urls", "modification_callbacks",
    "management", "num_form_tags", "num_meta_refresh",
    "num_external_iframe_src", "num_behavior", "notifications",
]

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
        ("svm", SVC(kernel="rbf", probability=True, class_weight="balanced", random_state=42))
    ])

    # Hyperparameter tuning
    param_grid = {
        "svm__C": [0.1, 1, 10, 100, 1000],
        # "svm__gamma": [1e-4, 1e-3, 1e-2, 1e-1, "scale"],
        "svm__gamma":[1e-4, 3e-4, 1e-3, 3e-3, 1e-2, 3e-2, 1e-1],
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
    proba = best_model.predict_proba(X_test)[:, 1]

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
        "model": best_model,
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


    # # Define the SVM gamma parameter range
    # param_range = np.logspace(-3, 3, 7)

    # # Calculate the validation curve for the SVM gamma parameter
    # train_scores, test_scores = validation_curve(SVC(kernel = 'rbf'), X_train, y_train, param_name = "gamma", param_range = param_range, cv = 5, error_score = 'raise')

    # # Calculate the mean and standard deviation of the training and testing scores
    # train_mean = np.mean(train_scores, axis = 1)
    # train_std = np.std(train_scores, axis=1)
    # test_mean = np.mean(test_scores, axis=1)
    # test_std = np.std(test_scores, axis=1)

    # print("train_mean:", train_mean, "train_std:", train_std, "test_mean:", test_mean, "test_std:", test_std)
    # C_range = np.logspace(-2, 10, 13)
    # gamma_range = np.logspace(-9, 3, 13)
    # param_grid = dict(gamma=gamma_range, C=C_range)
    # cv = StratifiedShuffleSplit(n_splits=5, test_size=0.2, random_state=42)
    # grid = GridSearchCV(SVC(), param_grid=param_grid, cv=cv)
    # grid.fit(X, y)

    # print(
    #     "The best parameters are %s with a score of %0.2f"
    #     % (grid.best_params_, grid.best_score_)
    # )


    # # Plot the validation curve
    # plt.title("Validation Curve for RBF SVM")
    # plt.xlabel("Gamma")
    # plt.ylabel("Score")
    # plt.ylim(0.0, 1.1)
    # lw = 2
    # plt.semilogx(param_range, train_mean, label="Training score",
    #             color="darkorange", lw=lw)
    # plt.fill_between(param_range, train_mean - train_std,
    #                 train_mean + train_std, alpha=0.2,
    #                 color="darkorange", lw=lw)
    # plt.semilogx(param_range, test_mean, label="Cross-validation score",
    #             color="navy", lw=lw)
    # plt.fill_between(param_range, test_mean - test_std,
    #                 test_mean + test_std, alpha=0.2,
    #                 color="navy", lw=lw)
    # plt.legend(loc="best")
    # plt.show()
