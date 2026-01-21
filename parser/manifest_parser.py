import json

# Go through the manifest file and extract important information


def analyzeManifest(manifest):
    # Open the manifest.json file in read mode
    with open(manifest, 'r') as manifest_file:
        # Parse the JSON-formatted string into a Python dictionary
        manifest_data = json.load(manifest_file)

        print(manifest_data['permissions'])
