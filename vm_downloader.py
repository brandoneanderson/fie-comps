#!/usr/bin/env python3
import os, re, time, zipfile, json, sys, subprocess
import requests
from urllib.parse import urlparse, parse_qs, unquote
import subprocess

from ML.download_mal_ext import *

DOWNLOAD_DIR = os.path.expanduser("~/fie-comps/parser/Extensions")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# >>> SET THIS to your real manager.py path on the VM <<<
MANAGER_PY = os.path.expanduser("~/fie-comps/parser/manager.py")
PYTHON = "python3"
# PYTHON = "/home/fiecomps/fie-comps/venv3139/bin/python"
# Use the VM venv python by default; allow override via env var if needed.
PYTHON = os.environ.get("FIECOMPS_PYTHON", "/home/fiecomps/fie-comps/venv3139/bin/python")


def extract_json_object_from_mixed_output(text: str):
    """
    Finds and parses the first valid JSON object in a string that may include
    extra junk lines before/after JSON.
    """
    text = (text or "").strip()
    if not text:
        raise json.JSONDecodeError("empty stdout", "", 0)

    decoder = json.JSONDecoder()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Scan for a JSON object starting at any '{'
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, end = decoder.raw_decode(text[i:])
            return obj
        except json.JSONDecodeError:
            continue

    raise json.JSONDecodeError("no JSON object found", text, 0)

def extract_ext_id(store_url: str) -> str:
    s = store_url.strip()

    # If user pasted just the ID
    if re.fullmatch(r"[a-p]{32}", s):
        return s

    # If there's an extension ID anywhere, grab it
    m = re.search(r"([a-p]{32})", s)
    if m:
        return m.group(1)

    # Try unwrapping wrapper URLs (google.com/url, etc.) and re-scan
    try:
        u = urlparse(s)
        qs = parse_qs(u.query or "")

        for key in ("q", "url", "u"):
            if key in qs and qs[key]:
                inner = unquote(qs[key][0]).strip()
                m2 = re.search(r"([a-p]{32})", inner)
                if m2:
                    return m2.group(1)
    except Exception:
        pass

    raise ValueError("Could not find extension id (32 chars a-p) in URL.")


def download_crx(ext_id: str, out_path: str) -> None:
    
    try:
        update_url = (
            "https://clients2.google.com/service/update2/crx"
            f"?response=redirect&prodversion=120.0&acceptformat=crx2,crx3"
            f"&x=id%3D{ext_id}%26installsource%3Dondemand%26uc"
        )
        r = requests.get(update_url, timeout=60)
        ct = (r.headers.get("content-type") or "").lower()
        if r.status_code != 200:
            raise RuntimeError(f"Download failed: HTTP {r.status_code}")
        if "text/html" in ct:
            raise RuntimeError("Got HTML instead of CRX (private/blocked extension?)")
        with open(out_path, "wb") as f:
            f.write(r.content)
    except:
        # update to actually grab versions instead of hardcoding one specific extension
        download_mal_ext(ext_id, '1.0')


def extract_crx_like_zip(crx_path: str, extract_dir: str) -> None:
    with open(crx_path, "rb") as f:
        data = f.read()
    sig = b"PK\x03\x04"
    idx = data.find(sig)
    if idx == -1:
        raise RuntimeError("Downloaded CRX did not contain a ZIP payload.")
    zip_path = crx_path + ".zip"
    with open(zip_path, "wb") as f:
        f.write(data[idx:])
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(extract_dir)


def run_manager(extract_dir: str) -> dict:
    """
    Run manager.py after download/extract.
    Returns:
      { ok: True, report: <dict> } if manager prints JSON
      or { ok: False, error: ..., raw_output: ... } otherwise
    """
    if not os.path.exists(MANAGER_PY):
        return {"ok": False, "error": f"manager.py not found at {MANAGER_PY}"}
    
    if not os.path.exists(PYTHON):
        return {"ok": False, "error": f"Python interpreter not found at {PYTHON}"}


    cmd = [PYTHON, MANAGER_PY, extract_dir]
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,   # 3 minutes, adjust if needed
        )
    except Exception as e:
        return {"ok": False, "error": f"Failed to run manager.py: {e}"}

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()

    if proc.returncode != 0:
        return {
            "ok": False,
            "error": f"manager.py exited with code {proc.returncode}",
            "stdout": stdout[:4000],
            "stderr": stderr[:4000],
        }

    # Try JSON parse
    try:
        report = extract_json_object_from_mixed_output(stdout)
        return {"ok": True, "report": report, "stderr": stderr[:2000]}
    except Exception:
        return {
            "ok": False,
            "error": "manager.py did not output valid JSON",
            "raw_output": stdout[:4000],
            "stderr": stderr[:4000],
        }



def main():
    if len(sys.argv) != 2:
        print(json.dumps({"detail": "usage: vm_downloader.py <store_url>"}))
        return 2

    store_url = sys.argv[1]
    ext_id = extract_ext_id(store_url)
    ts = time.strftime("%Y%m%d-%H%M%S")
    crx_path = os.path.join(DOWNLOAD_DIR, f"{ext_id}-{ts}.crx")
    extract_dir = os.path.join(DOWNLOAD_DIR, f"{ext_id}-{ts}")

    download_crx(ext_id, crx_path)
    extract_crx_like_zip(crx_path, extract_dir)

    #manager_result = run_manager(extract_dir)
    analysis = run_manager(extract_dir)

    print(json.dumps({
        "extension_id": ext_id,
        "crx_path": crx_path,
        "extract_dir": extract_dir,
        "message": "Downloaded and extracted on VM via SSH.",
        "analysis": analysis
    }))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"detail": str(e)}))
        sys.exit(1)

