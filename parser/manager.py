#This is the new verison

import os
import sys
import json
import traceback
from pathlib import Path

# Add project root (…/fie-comps) to Python path so `import ML` works
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
import re
from paths import *
import extension
from extractor import *
from Scanners.manifest_parser import * 
from analyzer import *
from Scanners.js_parser import *
from Scanners.css_parser import *
from Scanners.html_parser import *
#from Scanners.html_report import html_report_section
import joblib
import pandas as pd
from ML.scoring import risk_score_thresholded, risk_level, recommended_action, confidence_from_margin
from ML.vectorize import vectorizeExt



import re

def resolve_i18n_name(ext, extract_dir: Path) -> str:
    """
    If extension name looks like __MSG_key__, resolve it from _locales/*/messages.json.
    Prefer en / en_US / en_GB, else fall back to first locale found.
    """
    name = ext.getName() or ""
    m = re.match(r"^__MSG_(.+?)__$", name)
    if not m:
        return name

    key = m.group(1)
    locales_dir = extract_dir / "_locales"
    if not locales_dir.exists():
        return name

    preferred = ["en", "en_US", "en_GB"]
    locale_paths = []

    for loc in preferred:
        p = locales_dir / loc / "messages.json"
        if p.exists():
            locale_paths.append(p)

    # If no preferred locale exists, try any locale
    if not locale_paths:
        for p in locales_dir.glob("*/messages.json"):
            locale_paths.append(p)

    for p in locale_paths:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if key in data and "message" in data[key]:
                return data[key]["message"]
        except Exception:
            continue

    return name

# If you want logs, send them to stderr so stdout stays JSON-clean
def log(*args):
    print(*args, file=sys.stderr)

def vectorize_for_ml(ext) -> dict:
    all_features = {}
    # merge in the feature dicts your Extension already stores
    for d in [
        getattr(ext, "permissions", {}) or {},
        getattr(ext, "js_features", {}) or {},
        getattr(ext, "css_features", {}) or {},
        getattr(ext, "html_features", {}) or {},
    ]:
        all_features.update(d)
    return all_features


# SVM_BUNDLE = joblib.load(SVM_BUNDLE_PATH)
# SVM_MODEL = SVM_BUNDLE["model"]
# SVM_FEATURES = SVM_BUNDLE["feature_cols"]
# SVM_THRESHOLD = float(SVM_BUNDLE["threshold"])
def load_svm_bundle(bundle_path: str):
    bundle = joblib.load(bundle_path)
    return (
        bundle["model"],
        bundle["feature_cols"],
        float(bundle["threshold"])
    )


def predict_svm(ext, model, feature_cols, threshold) -> dict:
    feat = vectorizeExt(ext)

    X = pd.DataFrame([feat])

    # make sure all required feature columns exist
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
        "threshold": float(threshold),
        "confidence": confidence_from_margin(prob, threshold),
        "action": recommended_action(level),
    }

if __name__ == "__main__":
    # Expect: python3 manager.py /path/to/extracted_extension_dir
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "detail": "usage: manager.py <extract_dir>"}))
        sys.exit(2)

    extract_dir = Path(sys.argv[1]).expanduser().resolve()

    if not extract_dir.exists() or not extract_dir.is_dir():
        print(json.dumps({"ok": False, "detail": f"extract_dir not found or not a directory: {str(extract_dir)}"}))
        sys.exit(2)

    try:
        # Build Extension object for THIS extracted folder
        ext = extension.Extension(extract_dir)
        ext.setScriptsPaths()

        manifest_path = ext.getManifestPath()
        if not manifest_path:
            print(json.dumps({
                "ok": False,
                "detail": "No manifest found in extracted extension directory",
                "extract_dir": str(extract_dir),
            }))
            sys.exit(1)

        # Analyze manifest
        try:
            analyzeManifest(manifest_path, ext)
        except Exception as e:
            print(json.dumps({
                "ok": False,
                "detail": f"Failed to analyze manifest: {e}",
                "extract_dir": str(extract_dir),
            }))
            sys.exit(1)

        # Analyze files
        for allfiles in (ext.js_files, ext.html_files, ext.json_files, ext.css_files):
            for file in allfiles:
                try:
                    extractURLs(file, ext)
                    if file.suffix == ".js":
                        analyzeJS(file, ext)
                    elif file.suffix == ".css":
                        analyze_CSS(file, ext)
                    elif file.suffix in (".html", ".htm"):
                        analyze_HTML(file, ext)
                    # .json skip is fine
                except Exception as e:
                    # Don't crash whole run on one file; log and continue
                    log(f"[WARN] File analysis failed: {file} :: {e}")

        # Load ML bundle and predict
        if "SVM_BUNDLE_PATH" not in globals():
            print(json.dumps({"ok": False, "detail": "SVM_BUNDLE_PATH not defined in paths.py", "extract_dir": str(extract_dir)}))
            sys.exit(1)

        model, feature_cols, threshold = load_svm_bundle(SVM_BUNDLE_PATH)
        log("Loaded bundle:", SVM_BUNDLE_PATH, "num_features=", len(feature_cols), "threshold=", threshold)

        ml_pred = predict_svm(ext, model, feature_cols, threshold)

        resolved_name = resolve_i18n_name(ext, extract_dir)

        
        # Build JSON-safe output
        output = {
            "ok": True,
            "extension_name": resolved_name,
            #"extension_name": ext.getName(),
            "extract_dir": str(extract_dir),
            "prediction": ml_pred
        }

        output["html_features"] = getattr(ext, "html_features", None)
        output["html_examples"] = getattr(ext, "html_examples", None)

        # --- NEW: include manifest/js/css fields for UI tabs ---
        output["permissions"] = getattr(ext, "permissions", None)
        output["host_permissions"] = getattr(ext, "host_permissions", None)
        output["security_policy"] = getattr(ext, "security_policy", None)
        output["manifest_examples"] = getattr(ext, "manifest_examples", None)

        output["css_features"] = getattr(ext, "css_features", None)
        output["css_examples"] = getattr(ext, "css_examples", None)

        output["js_features"] = getattr(ext, "js_features", None)
        output["js_examples"] = getattr(ext, "js_examples", None)



        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "ok": False,
            "detail": str(e),
            "extract_dir": str(extract_dir),
        }))
        sys.exit(1)


