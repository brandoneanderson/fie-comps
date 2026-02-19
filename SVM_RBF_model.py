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

import json
from datetime import datetime

import matplotlib.pyplot as plt

from sklearn.metrics import (
    f1_score, precision_score, recall_score, accuracy_score,
    balanced_accuracy_score, matthews_corrcoef,
    brier_score_loss, log_loss
)
from sklearn.calibration import calibration_curve
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

K_BEST_FEATURES = [
    "avg_line_length",
    "specific_characters",
    "dynamic_code_gen_functions",
    "event_handlers",
    "DOM_operations",
    "keyword_density",
    "whitespace %",
    "DOM_change_sinks_density",
    "string_entropy",
    "word_size",
    "DOM_operations_density",
    "webRequestBlocking",
    "event_handlers_density",
    "DOM_change_sinks",
    "num_external_urls",
    "XMLHttpRequests_density",
    "num_script_tags",
    "num_script_src_attrs",
    "num_background_image",
    "storage",
    "All https domains",
    "XMLHttpRequests",
    "num_import_rules",
    "tabs",
    "webRequest",
    "modification_callbacks_density",
    "security_policy",
    "num_iframe_tags",
    "num_form_tags",
    "cookies",
    "notifications",
    "num_http_urls",
    "num_external_iframe_src",
    "modification_callbacks",
    "num_password_inputs",
    "num_behavior",
    "management",
    "All http domains",
    "num_inline_event_handlers"
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

    # annotate cells
    thresh = cm.max() / 2.0 if cm.max() > 0 else 0.5
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(
                j, i, format(cm[i, j], "d"),
                ha="center", va="center",
                color="white" if cm[i, j] > thresh else "black"
            )

    fig.tight_layout()
    fig.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def compute_threshold_bundle(y_true, proba):
    """
    Returns thresholds + predictions for:
      - 0.5
      - max-F1
      - Youden J (TPR-FPR)
    """
    # 0.5
    thr_05 = 0.5

    # max-F1 on PR curve thresholds
    precision, recall, thresholds = precision_recall_curve(y_true, proba)
    f1_scores = (2 * precision[:-1] * recall[:-1]) / (precision[:-1] + recall[:-1] + 1e-12)
    best_i = int(np.argmax(f1_scores))
    thr_f1 = float(thresholds[best_i])

    # Youden J
    fpr, tpr, thr = roc_curve(y_true, proba)
    youden = tpr - fpr
    thr_youden = float(thr[int(np.argmax(youden))])

    return {
        "thr_05": thr_05,
        "thr_f1": thr_f1,
        "thr_youden": thr_youden,
    }


def metrics_at_threshold(y_true, proba, thr):
    pred = (proba >= thr).astype(int)
    cm = confusion_matrix(y_true, pred)

    out = {
        "threshold": float(thr),
        "accuracy": _safe_float(accuracy_score(y_true, pred)),
        "balanced_accuracy": _safe_float(balanced_accuracy_score(y_true, pred)),
        "precision": _safe_float(precision_score(y_true, pred, zero_division=0)),
        "recall": _safe_float(recall_score(y_true, pred, zero_division=0)),
        "f1": _safe_float(f1_score(y_true, pred, zero_division=0)),
        "mcc": _safe_float(matthews_corrcoef(y_true, pred)),
        "confusion_matrix": cm.tolist(),
        "classification_report": classification_report(y_true, pred, digits=3, zero_division=0),
    }
    return out, pred, cm


def save_eval_artifacts(
    out_dir: Path,
    y_test,
    proba,
    best_params: dict,
    thresholds: dict,
    pred_05,
    pred_f1,
    pred_youden,
    cm_05,
    cm_f1,
    cm_youden,
):
    """
    Creates:
      - PNG graphs (roc.png, pr.png, calibration.png, threshold_f1.png, cm_*.png)
      - metrics.json
      - evaluation_report.pdf (single file with text + images)
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---------- Global (threshold-free) metrics ----------
    roc_auc = roc_auc_score(y_test, proba)
    pr_auc = average_precision_score(y_test, proba)

    # Calibration-ish metrics (need probabilities)
    brier = brier_score_loss(y_test, proba)
    ll = log_loss(y_test, np.vstack([1 - proba, proba]).T, labels=[0, 1])

    run_summary = {
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "roc_auc": float(roc_auc),
        "pr_auc": float(pr_auc),
        "brier": float(brier),
        "log_loss": float(ll),
        "best_params": best_params,
        "thresholds": thresholds,
    }

    # ---------- Curves ----------
    # ROC
    fpr, tpr, roc_thr = roc_curve(y_test, proba)
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

    # Precision-Recall
    prec, rec, pr_thr = precision_recall_curve(y_test, proba)
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

    # Calibration curve
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

    # Threshold vs F1 (on test)
    prec2, rec2, thr2 = precision_recall_curve(y_test, proba)
    f1s = (2 * prec2[:-1] * rec2[:-1]) / (prec2[:-1] + rec2[:-1] + 1e-12)
    thr_plot_path = out_dir / "threshold_f1.png"
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(thr2, f1s)
    ax.axvline(thresholds["thr_05"], linestyle="--")
    ax.axvline(thresholds["thr_f1"], linestyle="--")
    ax.axvline(thresholds["thr_youden"], linestyle="--")
    ax.set_title("Threshold vs F1 (test set)")
    ax.set_xlabel("Threshold")
    ax.set_ylabel("F1")
    fig.tight_layout()
    fig.savefig(thr_plot_path, dpi=200, bbox_inches="tight")
    plt.close(fig)

    # ---------- Confusion matrices ----------
    cm05_path = out_dir / "cm_thr_0_5.png"
    cmf1_path = out_dir / "cm_thr_max_f1.png"
    cmy_path  = out_dir / "cm_thr_youden.png"
    _plot_confusion_matrix(cm_05,    "Confusion Matrix @ thr=0.5", cm05_path)
    _plot_confusion_matrix(cm_f1,    f"Confusion Matrix @ thr={thresholds['thr_f1']:.4f} (max-F1)", cmf1_path)
    _plot_confusion_matrix(cm_youden,f"Confusion Matrix @ thr={thresholds['thr_youden']:.4f} (Youden)", cmy_path)

    # ---------- Per-threshold metric blocks ----------
    m05, _, _ = metrics_at_threshold(y_test, proba, thresholds["thr_05"])
    mf1, _, _ = metrics_at_threshold(y_test, proba, thresholds["thr_f1"])
    myd, _, _ = metrics_at_threshold(y_test, proba, thresholds["thr_youden"])

    run_summary["at_thresholds"] = {
        "thr_0_5": m05,
        "thr_max_f1": mf1,
        "thr_youden": myd,
    }

    # Save JSON
    json_path = out_dir / "metrics.json"
    json_path.write_text(json.dumps(run_summary, indent=2), encoding="utf-8")

    # ---------- PDF report ----------
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import inch

    pdf_path = out_dir / "evaluation_report.pdf"
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    W, H = letter

    def draw_kv(y, k, v):
        c.setFont("Helvetica-Bold", 10)
        c.drawString(0.75 * inch, y, f"{k}:")
        c.setFont("Helvetica", 10)
        c.drawString(2.2 * inch, y, str(v))

    # Page 1: headline + metrics
    c.setFont("Helvetica-Bold", 16)
    c.drawString(0.75 * inch, H - 0.9 * inch, "SVM (RBF) Evaluation Report")

    c.setFont("Helvetica", 10)
    c.drawString(0.75 * inch, H - 1.2 * inch, f"Created: {run_summary['created_at']}")

    y = H - 1.6 * inch
    draw_kv(y, "ROC-AUC", f"{roc_auc:.4f}"); y -= 0.22 * inch
    draw_kv(y, "PR-AUC (AP)", f"{pr_auc:.4f}"); y -= 0.22 * inch
    draw_kv(y, "Brier score", f"{brier:.4f}"); y -= 0.22 * inch
    draw_kv(y, "Log loss", f"{ll:.4f}"); y -= 0.35 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "Chosen Thresholds"); y -= 0.25 * inch
    c.setFont("Helvetica", 10)
    draw_kv(y, "thr=0.5", f"{thresholds['thr_05']:.4f}"); y -= 0.22 * inch
    draw_kv(y, "thr=max-F1", f"{thresholds['thr_f1']:.4f}"); y -= 0.22 * inch
    draw_kv(y, "thr=Youden J", f"{thresholds['thr_youden']:.4f}"); y -= 0.35 * inch

    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.75 * inch, y, "Best GridSearch Params"); y -= 0.25 * inch
    c.setFont("Helvetica", 9)
    # Wrap params over multiple lines if needed
    params_str = json.dumps(best_params, indent=2)
    for line in params_str.splitlines():
        c.drawString(0.9 * inch, y, line[:120])
        y -= 0.18 * inch
        if y < 1.0 * inch:
            c.showPage()
            y = H - 1.0 * inch

    c.showPage()

    # Page 2: curves
    c.setFont("Helvetica-Bold", 14)
    c.drawString(0.75 * inch, H - 0.8 * inch, "Curves")

    # Place 2 images per page if they fit
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

    # Page 4: confusion matrices
    c.setFont("Helvetica-Bold", 14)
    c.drawString(0.75 * inch, H - 0.8 * inch, "Confusion Matrices")
    place_img(cm05_path, H - 1.1 * inch)
    place_img(cmf1_path, H - 4.6 * inch)

    c.showPage()

    c.setFont("Helvetica-Bold", 14)
    c.drawString(0.75 * inch, H - 0.8 * inch, "Confusion Matrix (Youden J)")
    place_img(cmy_path, H - 1.1 * inch)

    c.save()

    return {
        "out_dir": str(out_dir),
        "pdf_path": str(pdf_path),
        "json_path": str(json_path),
        "images": [str(roc_path), str(pr_path), str(cal_path), str(thr_plot_path), str(cm05_path), str(cmf1_path), str(cmy_path)],
    }
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
        "svm__C": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "svm__gamma":[0.01, 0.02,0.025, 0.03, 0.035, 0.04, 0.045, 0.05, 0.055, 0.06],
        "svm__class_weight": [
            None,
            "balanced",
            # {0:1, 1:1.5},
            # {0:1, 1:2},
            # {0:1, 1:3},
            # {0:1, 1:4},
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

        # --- Build threshold set + per-threshold predictions ---
    thresholds = compute_threshold_bundle(y_test, proba)

    # predictions + confusion matrices
    m05, pred_05, cm_05 = metrics_at_threshold(y_test, proba, thresholds["thr_05"])
    mf1, pred_f1, cm_f1 = metrics_at_threshold(y_test, proba, thresholds["thr_f1"])
    myd, pred_youden, cm_youden = metrics_at_threshold(y_test, proba, thresholds["thr_youden"])

    # --- Save evaluation artifacts (graphs + PDF + JSON) ---
    EVAL_DIR = Path(MODEL_BUNDLE_PATH).parent / "eval_artifacts"
    saved = save_eval_artifacts(
        out_dir=EVAL_DIR,
        y_test=y_test,
        proba=proba,
        best_params=gs.best_params_,
        thresholds=thresholds,
        pred_05=pred_05,
        pred_f1=pred_f1,
        pred_youden=pred_youden,
        cm_05=cm_05,
        cm_f1=cm_f1,
        cm_youden=cm_youden,
    )

    print("\nSaved evaluation artifacts:")
    print("  PDF:", saved["pdf_path"])
    print("  JSON:", saved["json_path"])
    print("  Images:")
    for p in saved["images"]:
        print("   -", p)
   