import json

# Go through the manifest file and extract important information


def analyzeManifest(manifest, extClass):
    # Open the manifest.json file in read mode
    with open(manifest, 'r') as manifest_file:
        # Parse the JSON-formatted string into a Python dictionary
        manifest_data = json.load(manifest_file)
        extClass.name = manifest_data.get('name')
        print(extClass.name)
        extClass.permissions = manifest_data.get('permissions')
        extClass.version = manifest_data.get('version')
        extClass.host_permissions = manifest_data.get('host_permissions')
        if 'content_security_policy' in manifest_data:
            extClass.security_policy = True

def getExtensionName(manifest, extClass):
    # Open the manifest.json file in read mode
    with open(manifest, 'r') as manifest_file:
        # Parse the JSON-formatted string into a Python dictionary
        manifest_data = json.load(manifest_file)
        extClass.name = manifest_data.get('name')
