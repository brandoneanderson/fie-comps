# #This is the new verison

# import os
# import sys
# import json
# import traceback
# from pathlib import Path
# import re
# from paths import *
# import extension
# from extractor import *
# from Scanners.manifest_parser import * 
# from analyzer import *
# from Scanners.js_parser import *
# from Scanners.css_parser import *
# from Scanners.html_parser import *
# #from Scanners.html_report import html_report_section
# import joblib
# import pandas as pd
# from ML.scoring import risk_score_thresholded, risk_level, recommended_action, confidence_from_margin



# import re

# def resolve_i18n_name(ext, extract_dir: Path) -> str:
#     """
#     If extension name looks like __MSG_key__, resolve it from _locales/*/messages.json.
#     Prefer en / en_US / en_GB, else fall back to first locale found.
#     """
#     name = ext.getName() or ""
#     m = re.match(r"^__MSG_(.+?)__$", name)
#     if not m:
#         return name

#     key = m.group(1)
#     locales_dir = extract_dir / "_locales"
#     if not locales_dir.exists():
#         return name

#     preferred = ["en", "en_US", "en_GB"]
#     locale_paths = []

#     for loc in preferred:
#         p = locales_dir / loc / "messages.json"
#         if p.exists():
#             locale_paths.append(p)

#     # If no preferred locale exists, try any locale
#     if not locale_paths:
#         for p in locales_dir.glob("*/messages.json"):
#             locale_paths.append(p)

#     for p in locale_paths:
#         try:
#             data = json.loads(p.read_text(encoding="utf-8"))
#             if key in data and "message" in data[key]:
#                 return data[key]["message"]
#         except Exception:
#             continue

#     return name

# # If you want logs, send them to stderr so stdout stays JSON-clean
# def log(*args):
#     print(*args, file=sys.stderr)

# def vectorize_for_ml(ext) -> dict:
#     all_features = {}
#     # merge in the feature dicts your Extension already stores
#     for d in [
#         getattr(ext, "permissions", {}) or {},
#         getattr(ext, "js_features", {}) or {},
#         getattr(ext, "css_features", {}) or {},
#         getattr(ext, "html_features", {}) or {},
#     ]:
#         all_features.update(d)
#     return all_features


# # SVM_BUNDLE = joblib.load(SVM_BUNDLE_PATH)
# # SVM_MODEL = SVM_BUNDLE["model"]
# # SVM_FEATURES = SVM_BUNDLE["feature_cols"]
# # SVM_THRESHOLD = float(SVM_BUNDLE["threshold"])
# def load_svm_bundle():
#     bundle = joblib.load(SVM_BUNDLE_PATH)
#     return (
#         bundle["model"],
#         bundle["feature_cols"],
#         float(bundle["threshold"])
#     )

# def predict_svm(ext) -> dict:
#     feat = vectorize_for_ml(ext)

#     X = pd.DataFrame([feat])

#     # make sure all required feature columns exist
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
#         "threshold": float(threshold),
#         "confidence": confidence_from_margin(prob, threshold),
#         "action": recommended_action(level),
#     }

# if __name__ == "__main__":
#     # Expect: python3 manager.py /path/to/extracted_extension_dir
#     if len(sys.argv) != 2:
#         print(json.dumps({"ok": False, "detail": "usage: manager.py <extract_dir>"}))
#         sys.exit(2)

#     extract_dir = Path(sys.argv[1]).expanduser().resolve()

#     if not extract_dir.exists() or not extract_dir.is_dir():
#         print(json.dumps({"ok": False, "detail": f"extract_dir not found or not a directory: {str(extract_dir)}"}))
#         sys.exit(2)

#     try:
#         # Build Extension object for THIS extracted folder
#         ext = extension.Extension(extract_dir)
#         ext.setScriptsPaths()

#         manifest_path = ext.getManifestPath()
#         if not manifest_path:
#             print(json.dumps({
#                 "ok": False,
#                 "detail": "No manifest found in extracted extension directory",
#                 "extract_dir": str(extract_dir),
#             }))
#             sys.exit(1)

#         # Analyze manifest
#         try:
#             analyzeManifest(manifest_path, ext)
#         except Exception as e:
#             print(json.dumps({
#                 "ok": False,
#                 "detail": f"Failed to analyze manifest: {e}",
#                 "extract_dir": str(extract_dir),
#             }))
#             sys.exit(1)

#         # Analyze files
#         for allfiles in (ext.js_files, ext.html_files, ext.json_files, ext.css_files):
#             for file in allfiles:
#                 try:
#                     extractURLs(file, ext)
#                     if file.suffix == ".js":
#                         analyzeJS(file, ext)
#                     elif file.suffix == ".css":
#                         analyze_CSS(file, ext)
#                     elif file.suffix in (".html", ".htm"):
#                         analyze_HTML(file, ext)
#                     # .json skip is fine
#                 except Exception as e:
#                     # Don't crash whole run on one file; log and continue
#                     log(f"[WARN] File analysis failed: {file} :: {e}")

#         # Load ML bundle and predict
#         if "SVM_BUNDLE_PATH" not in globals():
#             fail(extract_dir, "SVM_BUNDLE_PATH not defined in paths.py")

#         model, feature_cols, threshold = load_svm_bundle(SVM_BUNDLE_PATH)
#         log("Loaded bundle:", SVM_BUNDLE_PATH, "num_features=", len(feature_cols), "threshold=", threshold)

#         ml_pred = predict_svm(ext, model, feature_cols, threshold)

#         resolved_name = resolve_i18n_name(ext, extract_dir)

        
#         # Build JSON-safe output
#         output = {
#             "ok": True,
#             "extension_name": resolved_name,
#             #"extension_name": ext.getName(),
#             "extract_dir": str(extract_dir),
#             "prediction": ml_pred
#         }

#         output["html_features"] = getattr(ext, "html_features", None)
#         output["html_examples"] = getattr(ext, "html_examples", None)

#         # --- NEW: include manifest/js/css fields for UI tabs ---
#         output["permissions"] = getattr(ext, "permissions", None)
#         output["host_permissions"] = getattr(ext, "host_permissions", None)
#         output["security_policy"] = getattr(ext, "security_policy", None)
#         output["manifest_examples"] = getattr(ext, "manifest_examples", None)

#         output["css_features"] = getattr(ext, "css_features", None)
#         output["css_examples"] = getattr(ext, "css_examples", None)

#         output["js_features"] = getattr(ext, "js_features", None)
#         output["js_examples"] = getattr(ext, "js_examples", None)



#         print(json.dumps(output))
#         sys.exit(0)

#     except Exception as e:
#         print(json.dumps({
#             "ok": False,
#             "detail": str(e),
#             "extract_dir": str(extract_dir),
#         }))
#         sys.exit(1)


#!/usr/bin/env python3
import os
import sys
import json
import traceback
from pathlib import Path
import re

from paths import *  # must define SVM_BUNDLE_PATH etc.

import extension
from extractor import extractURLs

from Scanners.manifest_parser import analyzeManifest
from Scanners.js_parser import analyzeJS
from Scanners.css_parser import analyze_CSS
from Scanners.html_parser import analyze_HTML

import joblib
import pandas as pd

from ML.scoring import (
    risk_score_thresholded,
    risk_level,
    recommended_action,
    confidence_from_margin,
)

# -------------------------
# Debug helpers
# -------------------------
DEBUG = os.environ.get("FIE_DEBUG", "0") == "1"

def log(*args):
    """Logs to stderr only when FIE_DEBUG=1 so stdout remains valid JSON."""
    if DEBUG:
        print(*args, file=sys.stderr, flush=True)

def fail(extract_dir: Path, detail: str, **extra):
    payload = {"ok": False, "detail": detail, "extract_dir": str(extract_dir)}
    payload.update(extra)
    print(json.dumps(payload))
    sys.exit(1)

# -------------------------
# i18n name resolver
# -------------------------
def resolve_i18n_name(ext, extract_dir: Path) -> str:
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

    if not locale_paths:
        locale_paths = list(locales_dir.glob("*/messages.json"))

    for p in locale_paths:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if key in data and "message" in data[key]:
                return data[key]["message"]
        except Exception:
            continue

    return name

# -------------------------
# ML utilities
# -------------------------
def vectorize_for_ml(ext) -> dict:
    """Merge the per-section feature dicts stored on ext into one flat dict."""
    all_features = {}
    for d in [
        getattr(ext, "permissions", {}) or {},
        getattr(ext, "js_features", {}) or {},
        getattr(ext, "css_features", {}) or {},
        getattr(ext, "html_features", {}) or {},
    ]:
        all_features.update(d)
    return all_features

def load_svm_bundle(bundle_path: str):
    bundle = joblib.load(bundle_path)
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    threshold = float(bundle["threshold"])
    return model, feature_cols, threshold

def predict_svm(ext, model, feature_cols, threshold) -> dict:
    feat = vectorize_for_ml(ext)
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
        "threshold": float(threshold),
        "confidence": confidence_from_margin(prob, threshold),
        "action": recommended_action(level),
    }

# -------------------------
# Main
# -------------------------
def main():
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "detail": "usage: manager.py <extract_dir>"}))
        return 2

    extract_dir = Path(sys.argv[1]).expanduser().resolve()
    if not extract_dir.exists() or not extract_dir.is_dir():
        print(json.dumps({"ok": False, "detail": f"extract_dir not found: {extract_dir}"}))
        return 2

    try:
        log("Starting manager.py")
        log("extract_dir:", extract_dir)

        # Build extension object
        ext = extension.Extension(extract_dir)
        ext.setScriptsPaths()

        manifest_path = ext.getManifestPath()
        if not manifest_path:
            fail(extract_dir, "No manifest found in extracted extension directory")

        log("manifest_path:", manifest_path)

        # Analyze manifest
        try:
            analyzeManifest(manifest_path, ext)
        except Exception as e:
            fail(extract_dir, f"Failed to analyze manifest: {e}")

        # Analyze files (don’t crash whole run on one file)
        total_files = 0
        for allfiles in (ext.js_files, ext.html_files, ext.json_files, ext.css_files):
            for file in allfiles:
                total_files += 1
                try:
                    extractURLs(file, ext)
                    if file.suffix == ".js":
                        analyzeJS(file, ext)
                    elif file.suffix == ".css":
                        analyze_CSS(file, ext)
                    elif file.suffix in (".html", ".htm"):
                        analyze_HTML(file, ext)
                except Exception as e:
                    log(f"[WARN] File analysis failed: {file} :: {e}")

        log("total_files_seen:", total_files)
        log("feature_sizes:",
            "permissions=", len(getattr(ext, "permissions", {}) or {}),
            "js=", len(getattr(ext, "js_features", {}) or {}),
            "css=", len(getattr(ext, "css_features", {}) or {}),
            "html=", len(getattr(ext, "html_features", {}) or {}),
        )

        # Load ML bundle and predict
        if "SVM_BUNDLE_PATH" not in globals():
            fail(extract_dir, "SVM_BUNDLE_PATH not defined in paths.py")

        model, feature_cols, threshold = load_svm_bundle(SVM_BUNDLE_PATH)
        log("Loaded bundle:", SVM_BUNDLE_PATH, "num_features=", len(feature_cols), "threshold=", threshold)

        ml_pred = predict_svm(ext, model, feature_cols, threshold)

        resolved_name = resolve_i18n_name(ext, extract_dir)

        # Output expected by UI
        output = {
            "ok": True,
            "extension_name": resolved_name,
            "extract_dir": str(extract_dir),
            "prediction": ml_pred,

            # These fields feed your UI tabs
            "permissions": getattr(ext, "permissions", None),
            "host_permissions": getattr(ext, "host_permissions", None),
            "security_policy": getattr(ext, "security_policy", None),
            "manifest_examples": getattr(ext, "manifest_examples", None),

            "html_features": getattr(ext, "html_features", None),
            "html_examples": getattr(ext, "html_examples", None),

            "css_features": getattr(ext, "css_features", None),
            "css_examples": getattr(ext, "css_examples", None),

            "js_features": getattr(ext, "js_features", None),
            "js_examples": getattr(ext, "js_examples", None),
        }

        print(json.dumps(output))
        return 0

    except Exception as e:
        tb = traceback.format_exc()
        payload = {
            "ok": False,
            "detail": str(e),
            "extract_dir": str(extract_dir),
        }
        if DEBUG:
            payload["traceback"] = tb
        else:
            payload["traceback"] = "Enable FIE_DEBUG=1 to see traceback"
        print(json.dumps(payload))
        return 1

if __name__ == "__main__":
    sys.exit(main())
