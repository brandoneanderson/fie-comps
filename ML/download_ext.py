import requests
import shutil
from pathlib import Path

'''
    Simple function to download an extension seperate from the website.
    Needs an extension ID and downloads .crx placing it into Extensions folder
'''

def download_crx(extension_id):
    # Grab path to where extensions folder is
    Extension_Folder_Path = Path.cwd() / "parser" / "Extensions"

    # construct url to extension via ID
    url = (
        "https://clients2.google.com/service/update2/crx"
        f"?response=redirect&prodversion=120.0"
        f"&acceptformat=crx2,crx3&x=id={extension_id}%26uc"
    )

    # unique path to extension in Extensions folder
    out_path = Extension_Folder_Path / f"{extension_id}.crx"

    # Capture already downloaded extensions
    if out_path.exists():
        print("Extension already downloaded!")
        return out_path

    # grab extension using requests
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    with open(out_path, "wb") as f:
        f.write(r.content)

    return out_path

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
# if __name__ == "__main__":
#     id = "phidhnmbkbkbkbknhldmpmnacgicphkf"
#     path = download_crx(id)
#     delete_file(path)