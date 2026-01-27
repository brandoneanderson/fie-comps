#!/usr/bin/env python3
import os, re, time, zipfile, json, sys
import requests

DOWNLOAD_DIR = os.path.expanduser("~/extension_downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def extract_ext_id(store_url: str) -> str:
    m = re.search(r"/detail/[^/]+/([a-p]{32})", store_url)
    if not m:
        m2 = re.fullmatch(r"([a-p]{32})", store_url.strip())
        if m2:
            return m2.group(1)
        raise ValueError("Could not find extension id (32 chars a-p) in URL.")
    return m.group(1)

def download_crx(ext_id: str, out_path: str) -> None:
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

    print(json.dumps({
        "extension_id": ext_id,
        "crx_path": crx_path,
        "extract_dir": extract_dir,
        "message": "Downloaded and extracted on VM via SSH."
    }))
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(json.dumps({"detail": str(e)}))
        sys.exit(1)
