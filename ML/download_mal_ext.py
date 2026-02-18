import requests
import shutil
from pathlib import Path

'''
    Simple function to download a malicious extension form chrome stats.
    Needs an extension ID and downloads .crx placing it into Extensions folder
'''

def download_mal_ext(extension_id, version):
    # Grab path to where extensions folder is
    Extension_Folder_Path = Path.cwd() / "parser" / "Extensions"
    # If folder doesn't exist, make it
    Extension_Folder_Path.mkdir(parents=True, exist_ok=True)

    # API endpoint
    url = "https://chrome-stats.com/api/download"

    # Query parameters
    params = {
        "id": f"{extension_id}",
        "type": "ZIP",  # or "CRX"
        "version": f"{version}"
    }

    # Headers (include your real API key)
    headers = {
        "accept": "application/zip",
        "x-api-key": "64cb4a8f-d1d3-48bf-8bc7-6d58400d306a"
    }

    # unique path to extension in Extensions folder
    out_path = Extension_Folder_Path / f"{extension_id}.zip"

    # Capture already downloaded extensions
    if out_path.exists():
        print("Extension already downloaded!")
        return out_path
    
    # Make request
    response = requests.get(url, params=params, headers=headers, timeout=30, allow_redirects=True)

    # Check response
    if response.status_code == 200:
        with open(out_path, "wb") as f:
            f.write(response.content)
        return out_path
    else:
        print("Error:", response.status_code)
        print(response.text)

def delete_file(path : Path):
    if path.is_file():
        path.unlink()
        print(f"File deleted: {path.name}")
    elif path.is_dir():
        shutil.rmtree(path)
        print(f"Directory deleted: {path.name}")
    else:
        print(f"Error: {path.name} not found")
    return

# TESTING FUNCTIONS
# ID is mybib
if __name__ == "__main__":
    id = "chmfnmjfghjpdamlofhlonnnnokkpbao"
    version = "1.0.3"
    path = download_mal_ext(id, version)
    delete_file(path)