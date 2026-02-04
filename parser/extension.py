from pathlib import Path
from Scanners.manifest_parser import * 
import os


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
        self.permissions = None
        self.version = None
        self.js_features = {
            "dynamic_code_gen_functions": 0, "whitespace %":0, 
            "avg line length":0, "specific characters":0, "word size":0,
            "string entropy":0, "DOM change methods":0, "event handlers":0,
            "HTTP scripts":0, "modifcation callbacks":0, "XMLHttpRequests":0,
            "keyword density":0}
        self.js_totals = {"total_chars": 0, "whitespace": 0, "specific_chars":0, "file_count":0, "total_lines": 0, "total_line_chars":0}
        self.html_features = None
        self.html_examples = None

        self.css_features = None
        self.security_policy = False
        self.host_permissions = None

        # List of urls & stuff
        self.urls = []

    def getName(self):
        """Utility function to return Extension filename"""
        return self.name
    
    def getFolderPath(self):
         """Utility function to return Extension folder path"""
         return self.folderpath
    
    def setScriptsPaths(self):
    #     """Utility function to search and record all filepaths to scripts (manifest, js, css, html) in appropraite attribute list"""

    # FOR NEW PYTHON
    #     # Iterate through all the files in the extension folder
    #     for dirpath, dirnames, filenames in self.folderpath.walk():
    #         for filename in filenames:
    #             full_path = dirpath / filename
    #             # Grabs each and every file according to file type and store into appropriate array
    #             if full_path.suffix == '.json':
    #                 # Record manifest path
    #                 if filename == 'manifest.json':
    #                     self.manifest = full_path
    #                     # Set appropriate extension name
    #                     getExtensionName(self.getManifestPath(), self)
    #                 else:
    #                     self.json_files.append(full_path)

    #             elif full_path.suffix in ('.html', '.htm'):
    #                 self.html_files.append(full_path)

    #             elif full_path.suffix == '.js':
    #                 self.js_files.append(full_path)
        # Iterate through all the files in the extension folder

        # FOR OLD PYTHON
        for dirpath, dirnames, filenames in self.folderpath.walk():
            for filename in filenames:
                full_path = dirpath / filename
                # Grabs each and every file according to file type and store into appropriate array
                if full_path.suffix == '.json':
                    # Record manifest path
                    if filename == 'manifest.json':
                        self.manifest = full_path
                        # Set appropriate extension name
                        getExtensionName(self.getManifestPath(), self)
                    else:
                        self.json_files.append(full_path)

                elif full_path.suffix in ('.html', '.htm'):
                    self.html_files.append(full_path)

                elif full_path.suffix == '.js':
                    # WILL SKIP BEAUTIFIED FILES
                    if full_path.name.endswith("_beautified.js"):
                        continue
                    else:
                        self.js_files.append(full_path)
                
    #             elif full_path.suffix == '.css':
    #                 self.css_files.append(full_path)
                
    #             elif full_path.suffix in ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.svg', '.gif'):
    #                 self.static_files.append(full_path)

    #             else:
    #                 self.other_files.append(full_path)
    #     return

    def setScriptsPaths(self):
        """
        Collect paths to JS/CSS/HTML/JSON files in the extracted extension folder.
        """
        import os
        from pathlib import Path

        if self.folderpath is None:
            raise ValueError("folderpath is None. Did extraction succeed?")

        self.js_files = []
        self.css_files = []
        self.html_files = []
        self.json_files = []

        for dirpath, dirnames, filenames in os.walk(self.folderpath):
            dirpath = Path(dirpath)
            for filename in filenames:
                f = dirpath / filename
                suffix = f.suffix.lower()

                if suffix == ".js":
                    self.js_files.append(f)
                elif suffix == ".css":
                    self.css_files.append(f)
                elif suffix in (".html", ".htm"):
                    self.html_files.append(f)
                elif suffix == ".json":
                    self.json_files.append(f)

    def getManifestPath(self):
        """Utility function to return Extension's Manifest folder path"""
        root = Path(self.folderpath)  # whatever you stored from extractor
        matches = list(root.rglob("manifest.json"))
        return str(matches[0]) if matches else None
        #return self.manifest
    
    def getPermissions(self):
        return self.permissions

    def setFinalJSTotals(self):
        total_chars = self.js_totals["total_chars"]

        if self.js_totals["total_lines"] > 0:
            self.js_features["avg line length"] = (
                self.js_totals["total_line_chars"] /
                self.js_totals["total_lines"]
            )
            
        if total_chars > 0:
            self.js_features["whitespace %"] = (self.js_totals["whitespace"] / total_chars)
            self.js_features["specific characters"] = (self.js_totals["specific_chars"] / total_chars)
        
        return