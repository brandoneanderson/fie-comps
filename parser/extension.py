from pathlib import Path
from parser.Scanners.manifest_parser import *
import os


class Extension:
    """
        Class to keep track of unpacked extension info such as names, folderpaths, and quick access to specific files
    """
    def __init__(self, folderpath : Path):
        if not folderpath.exists():
            raise FileNotFoundError(folderpath)
        
        # For keyword density in js analyzer
        keywords = {"this", "if", "var"}

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
            "dynamic_code_gen_functions": 0, "whitespace %": 0, 
            "avg_line_length": 0, "specific_characters": 0, "word_size": 0,
            "string_entropy": 0, "DOM_operations": 0, "DOM_change_sinks": 0, "event_handlers": 0,
            "HTTP_scripts": 0, "modification_callbacks": 0, "XMLHttpRequests": 0,
            "keyword_density": 0}
        self.js_totals = {"total_chars": 0, "whitespace": 0, "specific_chars":0, "file_count":0, "total_lines": 0, "total_line_chars":0, "total_words":0, "entropy_strings":0}
        self.js_keyword_den = {f"kw_{kw}": 0 for kw in keywords}
        self.html_features = {'num_script_tags': 0, 'num_script_src_attrs': 0, 'num_external_urls': 0}
        self.html_examples = None

        self.css_features = {'num_background_image': 0, 'num_behavior': 0, 'num_import_rules': 0, 'num_external_urls': 0}
        self.css_examples = None     
        self.js_examples = None      
        self.manifest_examples = None 

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
    
    # def setScriptsPaths(self):
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
        # for dirpath, dirnames, filenames in self.folderpath.walk():
            # for filename in filenames:
            #     full_path = dirpath / filename
            #     # Grabs each and every file according to file type and store into appropriate array
            #     if full_path.suffix == '.json':
            #         # Record manifest path
            #         if filename == 'manifest.json':
            #             self.manifest = full_path
            #             # Set appropriate extension name
            #             getExtensionName(self.getManifestPath(), self)
            #         else:
            #             self.json_files.append(full_path)

            #     elif full_path.suffix in ('.html', '.htm'):
            #         self.html_files.append(full_path)

            #     elif full_path.suffix == '.js':
            #         # WILL SKIP BEAUTIFIED FILES
            #         if full_path.name.endswith("_beautified.js"):
            #             continue
            #         else:
            #             self.js_files.append(full_path)
                
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
                    # WILL SKIP BEAUTIFIED FILES
                    if f.name.endswith("_beautified.js"):
                        continue
                    else:
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
        # Grab total words and chracters
        total_chars = self.js_totals["total_chars"]
        total_words = self.js_totals["total_words"]

        # Set average line length across all files
        if self.js_totals["total_lines"] > 0:
            self.js_features["avg_line_length"] = (
                self.js_totals["total_line_chars"] /
                self.js_totals["total_lines"]
            )
        
        # Set avg white space & and frequency of specific characters spotted
        if total_chars > 0:
            self.js_features["whitespace %"] = (self.js_totals["whitespace"] / total_chars)
            self.js_features["specific_characters"] = (self.js_totals["specific_chars"] / total_chars)

        # Set average word size & keyword density (sum of all tracked keywords / total words)
        # Set keyword density
        if total_words > 0:
            self.js_features["word_size"] = self.js_features["word_size"] / total_words
            total_kw_count = sum(self.js_keyword_den.values())
            self.js_features["keyword_density"] = total_kw_count / total_words

        # Set average string entropy
        if self.js_totals.get("entropy_strings", 0) > 0:
            self.js_features["string_entropy"] = (self.js_features["string_entropy"] / self.js_totals["entropy_strings"])
        else:
            self.js_features["avg_string_entropy"] = 0

        return
    
    def safe_div(self, n, d):
        if d > 0:
            return n/d
        else:
            return 0.0
    
    def normalizeJSBehavior(self):
        lines = self.js_totals["total_lines"]

        self.js_features["DOM_operations_density"] = self.safe_div(self.js_features["DOM_operations"], lines)

        self.js_features["DOM_change_sinks_density"] = self.safe_div(self.js_features["DOM_change_sinks"], lines)

        self.js_features["XMLHttpRequests_density"] = self.safe_div(self.js_features["XMLHttpRequests"], lines)

        self.js_features["event_handlers_density"] = self.safe_div(self.js_features["event_handlers"], lines)

        self.js_features["modification_callbacks_density"] = self.safe_div(self.js_features["modification_callbacks"], lines)

        self.js_features["HTTP_scripts_density"] = self.safe_div(self.js_features["HTTP_scripts"], lines)


    def setVulnerablePermissions(self):
        permissions = self.permissions
        host_perms = self.host_permissions
        sec_policy = self.security_policy

        vulnerable_perm = {"All http domains": 0, "All https domains": 0, "webRequest": 0,
                           "webRequestBlocking": 0, "tabs": 0, "storage": 0, "notifications": 0,
                           "cookies":0, "management": 0, "contextmenus": 0, "security_policy": 0}
        
        # Set permissions found to true
        for perm in permissions:
            if perm in vulnerable_perm:
                vulnerable_perm[perm] = 1
        
        if host_perms != None:
            # Set any host permissions found
            for host in host_perms:
                if host.startswith("http://") and "*" in host:
                    vulnerable_perm["All http domains"] = 1
                if host.startswith("https://") and "*" in host:
                    vulnerable_perm["All https domains"] = 1
        
        # Set security policy flag
        if sec_policy:
            vulnerable_perm["security_policy"] = 1
        
        # Set final permissions dict
        self.permissions = vulnerable_perm

        return
    
    def setFinalValues(self):
        self.setFinalJSTotals()
        self.normalizeJSBehavior()
        self.setVulnerablePermissions()