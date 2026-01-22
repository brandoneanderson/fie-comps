from pathlib import Path

class Extension:
    """
        Class to keep track of unpacked extension info such as names, folderpaths, and quick access to specific files
    """
    def __init__(self, folderpath : Path):
        if not folderpath.exists():
            raise FileNotFoundError(folderpath)

        # Extension file paths & identifiers
        self.name = folderpath.name
        self.folderpath = folderpath

        # Manifest important
        self.manifest = None

        # List of all files found in extension
        self.html_files = []
        self.js_files = []
        self.json_files = []
        self.css_files = []
        self.static_files = []
        self.other_files = []

        # Extension Permissions and Calls
        self.permissions = []
        self.version = None
        self.js_features = []
        self.html_features = []
        self.css_features = []
        self.security_policy = False
        self.host_permissions = []

        # List of urls & stuff
        self.urls = []

    def getName(self):
        """Utility function to return Extension filename"""
        return self.name
    
    def getFolderPath(self):
         """Utility function to return Extension folder path"""
         return self.folderpath
    
    def setScriptsPaths(self):
        """Utility function to search and record all filepaths to scripts (manifest, js, css, html) in appropraite attribute list"""

        # Iterate through all the files in the extension folder
        for dirpath, dirnames, filenames in self.folderpath.walk():
            for filename in filenames:
                full_path = dirpath / filename
                # Grabs each and every file according to file type and store into appropriate array
                if full_path.suffix == '.json':
                    # Record manifest path
                    if filename == 'manifest.json':
                        self.manifest = full_path
                    else:
                        self.json_files.append(full_path)

                elif full_path.suffix in ('.html', '.htm'):
                    self.html_files.append(full_path)

                elif full_path.suffix == '.js':
                    self.js_files.append(full_path)
                
                elif full_path.suffix == '.css':
                    self.css_files.append(full_path)
                
                elif full_path.suffix in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.svg', '.gif'):
                    self.static_files.append(full_path)

                else:
                    self.other_files.append(full_path)
        return

    def getManifestPath(self):
        """Utility function to return Extension's Manifest folder path"""
        return self.manifest
    
    def getPermissions(self):
        return self.permissions