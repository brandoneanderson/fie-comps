import json
from pathlib import Path

# Go through the manifest file and extract important information

def _load_manifest_json(path):
    """
    Load manifest.json robustly. Some manifests are UTF-16 or include a BOM.
    """
    raw = Path(path).read_bytes()
    for enc in ("utf-8", "utf-8-sig", "utf-16", "utf-16-le", "utf-16-be", "latin-1"):
        try:
            return json.loads(raw.decode(enc))
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue
    return json.loads(raw.decode("utf-8", errors="replace"))

def analyzeManifest(manifest, extClass):
    # Open the manifest.json file in read mode
    try:
        with open(manifest, 'r') as manifest_file:
            # Parse the JSON-formatted string into a Python dictionary
            manifest_data = _load_manifest_json(manifest)
            extClass.name = manifest_data.get('name')
            extClass.permissions = manifest_data.get('permissions')
            extClass.version = manifest_data.get('version')
            extClass.host_permissions = manifest_data.get('host_permissions')
            if 'content_security_policy' in manifest_data:
                extClass.security_policy = True
            else:
                extClass.security_policy = False
    except FileNotFoundError:
        print(f"Error: The file {manifest} was not found.")
    except Exception as e:
        print(f"An error ocurred: {e}")


def getExtensionName(manifest, extClass):
    # Open the manifest.json file in read mode
    with open(manifest, 'r') as manifest_file:
        # Parse the JSON-formatted string into a Python dictionary
        manifest_data = _load_manifest_json(manifest)
        extClass.name = manifest_data.get('name')
        return extClass.name
