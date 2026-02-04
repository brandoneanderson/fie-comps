#This is the new verison

import sys, json
from pathlib import Path

import extension
from extractor import *
from Scanners.manifest_parser import * 
from analyzer import *
from Scanners.js_parser import *
from Scanners.css_parser import *
from Scanners.html_parser import *
from Scanners.html_report import html_report_section


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

        # Score & prediction
        prediction = Score_Report(ext)
        prediction.predict()
        
        resolved_name = resolve_i18n_name(ext, extract_dir)
        
        # Build JSON-safe output
        output = {
            "ok": True,
            "extension_name": resolved_name,
            #"extension_name": ext.getName(),
            "extract_dir": str(extract_dir),
            "prediction": prediction.PREDICTION,
        }

        # if  Extension class stores useful structured fields, include them.
        # Only include JSON-serializable values.
        #
        # Example ideas
        # output["permissions"] = getattr(ext, "permissions", None)
        # output["host_permissions"] = getattr(ext, "host_permissions", None)
        # output["urls_found"] = list(getattr(ext, "urls", []))  # if it’s a set
        
        # Include HTML report + structured data in JSON for UI
        try:
            output["html_report"] = html_report_section(ext)
        except Exception as e:
            output["html_report"] = None
            log(f"[WARN] Could not build html_report: {e}")

        output["html_features"] = getattr(ext, "html_features", None)
        output["html_examples"] = getattr(ext, "html_examples", None)
        
        # Also print to stderr for terminal debugging (won't break JSON stdout)
        try:
            log("\n" + output["html_report"] + "\n")
        except Exception:
            pass


        print(json.dumps(output))
        sys.exit(0)

    except Exception as e:
        print(json.dumps({
            "ok": False,
            "detail": str(e),
            "extract_dir": str(extract_dir),
        }))
        sys.exit(1)
