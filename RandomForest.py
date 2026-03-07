from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_absolute_error, f1_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import json
from datetime import datetime
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_auc_score, average_precision_score,
    precision_recall_curve, roc_curve,
    accuracy_score, balanced_accuracy_score,
    precision_score, recall_score, f1_score,
    matthews_corrcoef, brier_score_loss, log_loss
)
from sklearn.calibration import calibration_curve
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from paths import *

# Paper guide
'''
    1. Optimize the number of trees in the forest that is used to contruct the RF
        a. Done with Out-of-bag error (which calculates the misclassification probability for out-of-bag observations in the training set)
        b. varying number of trees from 10 to 300 (they found 250 to be perfect for them)
    
    2. Run RF with optimized number of trees to calcultae importance score for each feature
        a. Calculate the importance score of each of the n features, where n = 51
        b. Rank the n features by the importance score in decreasing order
        c. Apply the first k features to the RF classifer, for k = 1 to n, and select the features involved
            in the classifier producing the lowest mean absolute error (MAE)
    
    OUTPUT: k features producing lowest MAE (mean absolute error)

    NOT DONE HERE, BUT WHAT WE DO WITH OUTPUT
    3. Feed features into SVM-RBF
'''

def randomForest(X, y):
    # Grab optimal tree count
    tree_count = compute_optimized_tree_count(X, y)

    # Grab optimal k best features using k-fold to avoid data leakage
    best_k_features_size, error_scores = find_best_k_features_kfold(X, y, tree_count)

    # Grab k-best features on entire dataset

    print("Best k feature size:", best_k_features_size)
    print("Error scores:", error_scores)
    print("Best error score:", error_scores[best_k_features_size])

    # Plot MAE vs number of selected features
    # plt.plot(range(1, len(error_scores)+1), error_scores)
    # plt.xlabel("Number of Features")
    # plt.ylabel("Cross-Validated MAE")
    # plt.title("MAE vs Number of Selected Features")
    # plt.show()

    optimized_features = get_top_k_features(X, y, tree_count, best_k_features_size)

    final_rf = RandomForestClassifier(n_estimators=tree_count, random_state=42, n_jobs=-1)
    final_rf.fit(X,y)

    return optimized_features, final_rf

def compute_optimized_tree_count(X, y):
    '''
        Purpose: Find optimal number of trees to construct our RF
        Why this works: OOB error, calculates the misclassification prob. for out-of-bag
                        observations in the training set. Get lowest error
    '''
    # Set up params
    min_trees = 15
    max_trees = 500
    trees_range = range(min_trees, max_trees + 1, 10)
    oob_errors = []

    # Loop through each tree count and find OOB
    for n_tree in trees_range:
        # Create a random forest for given tree count, record OOB score
        rf = RandomForestClassifier(n_estimators = n_tree, oob_score = True, bootstrap = True, random_state = 42, n_jobs = -1)
        rf.fit(X, y)

        oob_error = 1 - rf.oob_score_
        oob_errors.append(oob_error)

    # Find best tree count that minimizes OOB
    best_trees = trees_range[oob_errors.index(min(oob_errors))]
    print(f"Optimal number of trees based on OOB error: {best_trees}")

    # Plot results to find where error stabilizes
    # plt.plot(trees_range, oob_errors)
    # plt.xlabel("Number of Trees (n_estimators)")
    # plt.ylabel("OOB Error Rate")
    # plt.title("OOB Error Rate vs. Number of Trees")
    # plt.show()

    return best_trees

def find_best_k_features_kfold(X, y, tree_count):
    error_scores = []

    # Ensure each fold contains same percentage of samples for each class as the complete dataset
    skf = StratifiedKFold(n_splits = 5, shuffle = True, random_state = 42)

    # number of columns in the dataset
    n_features = X.shape[1]

    # Iterate through diff sized subsets of features
    for feature_subset_size in range(1, n_features + 1):
        fold_errors = []

        # Create train and val data for each fold
        for train_idx, val_idx in skf.split(X, y):
            X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
            y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

            # Train rf only on training fold
            rf = RandomForestClassifier(n_estimators=tree_count,random_state=42,n_jobs=-1)
            rf.fit(X_train, y_train)

            # Rank features inside fold
            importances = rf.feature_importances_
            ranked_features = np.argsort(importances)[::-1]

            # Best k-features in this fold
            selected_features = ranked_features[:feature_subset_size]

            # retrain using only top-k
            rf_k = RandomForestClassifier(n_estimators=tree_count,random_state=42,n_jobs=-1)
            rf_k.fit(X_train.iloc[:, selected_features], y_train)

            # Store predictions
            preds = rf_k.predict(X_val.iloc[:, selected_features])

            # Store MAE errors for each fold
            fold_errors.append(mean_absolute_error(y_val, preds))

        # Append average of fold errors
        error_scores.append(np.mean(fold_errors))
    
    # Grab optimal k features that return lowest score
    optimal_k = np.argmin(error_scores) + 1

    return optimal_k, error_scores

def get_top_k_features(X, y, tree_count, k):
    rf = RandomForestClassifier(n_estimators = tree_count, random_state = 42, n_jobs = -1)
    rf.fit(X,y)

    # Get feature importances
    importances = rf.feature_importances_

    # Order them in descending order
    ranked_indices = np.argsort(importances)[::-1]

    # select top-k indices
    # top_k_indices = ranked_indices[:k]

    # GRAB EVERYTHING
    top_k_indices = ranked_indices

    # Grab top indices and their attached value of importance
    top_features_dict = {}

    for index in top_k_indices:
        top_features_dict[index] = importances[index]

    print(top_features_dict)

    import sys

    # Store original standard output
    original_stdout = sys.stdout

    with open('ALL_FEATURES_RANKED.txt', 'w') as f:
        # Redirect standard output to the file
        sys.stdout = f
        print(top_features_dict)

    # Get feature names of top-k indices
    top_k_feature_names = X.columns[top_k_indices]

    return top_k_feature_names

def _plot_confusion_matrix(cm, title, out_path, class_names=("Benign (0)", "Malicious (1)")):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    im = ax.imshow(cm, interpolation="nearest")
    ax.set_title(title)
    plt.colorbar(im, ax=ax)

    tick_marks = np.arange(len(class_names))
    ax.set_xticks(tick_marks)
    ax.set_yticks(tick_marks)
    ax.set_xticklabels(class_names, rotation=30, ha="right")
    ax.set_yticklabels(class_names)

    ax.set_ylabel("True label")
    ax.set_xlabel("Predicted label")

    thresh = cm.max() / 2.0 if cm.max() > 0 else 0.5
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, str(cm[i, j]),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")

    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def compute_thresholds(y_true, proba):
    # 0.5
    thr_05 = 0.5

    # max-F1 threshold
    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    f1s = (2 * precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-12)
    i = int(np.argmax(f1s))
    thr_f1 = float(thresholds[i])

    # Youden J
    fpr, tpr, thr = roc_curve(y_true, proba)
    i2 = int(np.argmax(tpr - fpr))
    thr_youden = float(thr[i2])

    return {"thr_05": thr_05, "thr_f1": thr_f1, "thr_youden": thr_youden}


def metrics_at_threshold(y_true, proba, thr):
    pred = (proba >= thr).astype(int)
    cm = confusion_matrix(y_true, pred)
    return {
        "threshold": float(thr),
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "mcc": float(matthews_corrcoef(y_true, pred)),
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(y_true, pred, digits=3, zero_division=0),
    }, pred, cm


def save_rf_eval_artifacts(out_dir: Path, y_test, proba, rf_params: dict, selected_features, thresholds):
    out_dir.mkdir(parents=True, exist_ok=True)

    roc_auc = roc_auc_score(y_test, proba)
    pr_auc = average_precision_score(y_test, proba)
    brier = brier_score_loss(y_test, proba)
    ll = log_loss(y_test, np.vstack([1 - proba, proba]).T, labels=[0, 1])

    # Curves
    fpr, tpr, _ = roc_curve(y_test, proba)
    roc_path = out_dir / "roc.png"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(fpr, tpr)
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.set_title(f"ROC Curve (AUC={roc_auc:.4f})")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    fig.tight_layout()
    fig.savefig(roc_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    prec, rec, thr_pr = precision_recall_curve(y_test, proba)
    pr_path = out_dir / "pr.png"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(rec, prec)
    ax.set_title(f"Precision-Recall Curve (AP={pr_auc:.4f})")
    ax.set_xlabel("Recall")
    ax.set_ylabel("Precision")
    fig.tight_layout()
    fig.savefig(pr_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    frac_pos, mean_pred = calibration_curve(y_test, proba, n_bins=10, strategy="uniform")
    cal_path = out_dir / "calibration.png"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(mean_pred, frac_pos, marker="o")
    ax.plot([0, 1], [0, 1], linestyle="--")
    ax.set_title("Calibration Curve")
    ax.set_xlabel("Mean predicted probability")
    ax.set_ylabel("Fraction of positives")
    fig.tight_layout()
    fig.savefig(cal_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Threshold vs F1
    f1s = (2 * prec[:-1] * rec[:-1]) / (prec[:-1] + rec[:-1] + 1e-12)
    thr_plot_path = out_dir / "threshold_f1.png"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(thr_pr, f1s)
    ax.axvline(thresholds["thr_05"], linestyle="--")
    ax.axvline(thresholds["thr_f1"], linestyle="--")
    ax.axvline(thresholds["thr_youden"], linestyle="--")
    ax.set_title("Threshold vs F1 (test set)")
    ax.set_xlabel("Threshold")
    ax.set_ylabel("F1")
    fig.tight_layout()
    fig.savefig(thr_plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # Confusion matrices
    m05, _, cm05 = metrics_at_threshold(y_test, proba, thresholds["thr_05"])
    mf1, _, cmf1 = metrics_at_threshold(y_test, proba, thresholds["thr_f1"])
    myd, _, cmyd = metrics_at_threshold(y_test, proba, thresholds["thr_youden"])

    cm05_path = out_dir / "cm_thr_0_5.png"
    cmf1_path = out_dir / "cm_thr_max_f1.png"
    cmy_path  = out_dir / "cm_thr_youden.png"
    _plot_confusion_matrix(cm05, "Confusion Matrix @ thr=0.5", cm05_path)
    _plot_confusion_matrix(cmf1, f"Confusion Matrix @ thr={thresholds['thr_f1']:.4f} (max-F1)", cmf1_path)
    _plot_confusion_matrix(cmyd, f"Confusion Matrix @ thr={thresholds['thr_youden']:.4f} (Youden)", cmy_path)

    summary = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "brier": float(brier),
        "log_loss": float(ll),
        "rf_params": rf_params,
        "selected_features": list(map(str, selected_features)),
        "thresholds": thresholds,
        "at_thresholds": {
            "thr_0_5": m05,
            "thr_max_f1": mf1,
            "thr_youden": myd,
        },
        "artifacts": {
            "roc": str(roc_path),
            "pr": str(pr_path),
            "calibration": str(cal_path),
            "threshold_f1": str(thr_plot_path),
            "cm_thr_0_5": str(cm05_path),
            "cm_thr_max_f1": str(cmf1_path),
            "cm_thr_youden": str(cmy_path),
        }
    }

    json_path = out_dir / "metrics.json"
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    # Try PDF, fallback to HTML
    pdf_path = out_dir / "evaluation_report.pdf"
    html_path = out_dir / "evaluation_report.html"

    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib.units import inch

        c = canvas.Canvas(str(pdf_path), pagesize=letter)
        W, H = letter

        c.setFont("Helvetica-Bold", 16)
        c.drawString(0.75 * inch, H - 0.9 * inch, "RandomForest Evaluation Report")
        c.setFont("Helvetica", 10)
        c.drawString(0.75 * inch, H - 1.2 * inch, f"Created: {summary['created_at']}")

        y = H - 1.6 * inch
        def kv(k, v):
            nonlocal y
            c.setFont("Helvetica-Bold", 10); c.drawString(0.75 * inch, y, f"{k}:")
            c.setFont("Helvetica", 10); c.drawString(2.3 * inch, y, str(v))
            y -= 0.22 * inch

        kv("ROC-AUC", f"{roc_auc:.4f}")
        kv("PR-AUC (AP)", f"{pr_auc:.4f}")
        kv("Brier", f"{brier:.4f}")
        kv("Log loss", f"{ll:.4f}")
        y -= 0.2 * inch
        kv("thr=0.5", f"{thresholds['thr_05']:.4f}")
        kv("thr=max-F1", f"{thresholds['thr_f1']:.4f}")
        kv("thr=Youden", f"{thresholds['thr_youden']:.4f}")

        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.75 * inch, H - 0.8 * inch, "Curves")

        def place_img(img_path, top_y):
            c.drawImage(str(img_path), 0.75 * inch, top_y - 3.2 * inch, width=7.0 * inch, height=3.0 * inch, preserveAspectRatio=True, anchor='sw')

        place_img(roc_path, H - 1.1 * inch)
        place_img(pr_path,  H - 4.6 * inch)

        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.75 * inch, H - 0.8 * inch, "Calibration + Thresholding")
        place_img(cal_path, H - 1.1 * inch)
        place_img(thr_plot_path, H - 4.6 * inch)

        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.75 * inch, H - 0.8 * inch, "Confusion Matrices")
        place_img(cm05_path, H - 1.1 * inch)
        place_img(cmf1_path, H - 4.6 * inch)

        c.showPage()
        c.setFont("Helvetica-Bold", 14)
        c.drawString(0.75 * inch, H - 0.8 * inch, "Confusion Matrix (Youden)")
        place_img(cmy_path, H - 1.1 * inch)

        c.save()
        report_path = pdf_path
    except Exception:
        # HTML fallback (no extra deps)
        html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>RandomForest Evaluation Report</title>
  <style>
    body {{ font-family: -apple-system, system-ui, sans-serif; margin: 24px; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 8px; padding: 6px; }}
    code, pre {{ background: #f6f8fa; padding: 10px; border-radius: 8px; display: block; overflow-x: auto; }}
  </style>
</head>
<body>
<h1>RandomForest Evaluation Report</h1>
<p><b>Created:</b> {summary["created_at"]}</p>

<h2>Summary metrics</h2>
<ul>
  <li><b>ROC-AUC:</b> {roc_auc:.4f}</li>
  <li><b>PR-AUC (AP):</b> {pr_auc:.4f}</li>
  <li><b>Brier:</b> {brier:.4f}</li>
  <li><b>Log loss:</b> {ll:.4f}</li>
</ul>

<h2>Thresholds</h2>
<ul>
  <li>thr=0.5: {thresholds["thr_05"]:.4f}</li>
  <li>thr=max-F1: {thresholds["thr_f1"]:.4f}</li>
  <li>thr=Youden: {thresholds["thr_youden"]:.4f}</li>
</ul>

<h2>Plots</h2>
<div class="grid">
  <div><h3>ROC</h3><img src="{roc_path.name}"/></div>
  <div><h3>PR</h3><img src="{pr_path.name}"/></div>
  <div><h3>Calibration</h3><img src="{cal_path.name}"/></div>
  <div><h3>Threshold vs F1</h3><img src="{thr_plot_path.name}"/></div>
  <div><h3>CM @ 0.5</h3><img src="{cm05_path.name}"/></div>
  <div><h3>CM @ max-F1</h3><img src="{cmf1_path.name}"/></div>
  <div><h3>CM @ Youden</h3><img src="{cmy_path.name}"/></div>
</div>

<h2>Params + selected features</h2>
<pre>{json.dumps(rf_params, indent=2)}</pre>
<pre>{json.dumps(list(map(str, selected_features)), indent=2)}</pre>

<p>Full metrics saved to <code>metrics.json</code>.</p>
</body>
</html>
"""
        (out_dir / roc_path.name).write_bytes(Path(roc_path).read_bytes())
        (out_dir / pr_path.name).write_bytes(Path(pr_path).read_bytes())
        (out_dir / cal_path.name).write_bytes(Path(cal_path).read_bytes())
        (out_dir / thr_plot_path.name).write_bytes(Path(thr_plot_path).read_bytes())
        (out_dir / cm05_path.name).write_bytes(Path(cm05_path).read_bytes())
        (out_dir / cmf1_path.name).write_bytes(Path(cmf1_path).read_bytes())
        (out_dir / cmy_path.name).write_bytes(Path(cmy_path).read_bytes())

        html_path.write_text(html, encoding="utf-8")
        report_path = html_path

    return {
        "out_dir": str(out_dir),
        "report_path": str(report_path),
        "json_path": str(json_path),
    }

def train_and_evaluate_rf(df, label_col="label", out_dir=Path("rf_eval_artifacts")):
    y = df[label_col].astype(int)
    X = df.drop(columns=[label_col])

    # make sure numeric
    X = X.apply(pd.to_numeric, errors="coerce").fillna(0.0)

    # split for final honest evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # --- Your RF optimization happens ONLY on training split ---
    tree_count = compute_optimized_tree_count(X_train, y_train)
    best_k, _ = find_best_k_features_kfold(X_train, y_train, tree_count)
    selected_features = get_top_k_features(X_train, y_train, tree_count, best_k)

    # --- Train final RF using selected features ---
    rf = RandomForestClassifier(
        n_estimators=tree_count,
        random_state=42,
        n_jobs=-1,
        class_weight="balanced"   # optional but usually helpful
    )
    rf.fit(X_train[selected_features], y_train)

    proba = rf.predict_proba(X_test[selected_features])[:, 1]

    thresholds = compute_thresholds(y_test, proba)
    saved = save_rf_eval_artifacts(
        out_dir=out_dir,
        y_test=y_test,
        proba=proba,
        rf_params=rf.get_params(),
        selected_features=selected_features,
        thresholds=thresholds
    )

    print("Saved RF evaluation to:")
    print("  Report:", saved["report_path"])
    print("  JSON:", saved["json_path"])
    print("  Folder:", saved["out_dir"])

    return rf, selected_features, thresholds, saved
if __name__ == "__main__":
    df = pd.read_csv(TRAINING_CSV)
    rf_model, rf_features, rf_thresholds, rf_saved = train_and_evaluate_rf(
        df=df,
        label_col="label",
        out_dir=Path("ML/models/rf_eval_artifacts")
    )