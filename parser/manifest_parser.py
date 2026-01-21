import json

# Go through the manifest file and extract important information


def analyzeManifest(manifest, extClass):
    # Open the manifest.json file in read mode
    with open(manifest, 'r') as manifest_file:
        # Parse the JSON-formatted string into a Python dictionary
        manifest_data = json.load(manifest_file)

        extClass.permissions = manifest_data['permissions']
        extClass.version = manifest_data['version']
        if 'content_security_policy' in manifest_data:
            extClass.security_policy = True
