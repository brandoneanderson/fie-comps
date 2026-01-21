from pathlib import Path

class Extension:
    """
        Class to keep track of unpacked extension info such as names, folderpaths, and quick access to specific files
    """
    def __init__(self, folderpath : Path):
        if not folderpath.exists():
            raise FileNotFoundError(folderpath)

        self.name = folderpath.name
        self.folderpath = folderpath
        
        self.manifest = None
        self.service_worker = None
        self.index = None

    def getName(self):
        """Utility function to return Extension filename"""
        return self.name
    
    def getFolderPath(self):
         """Utility function to return Extension folder path"""
         return self.folderpath
    
    def setScriptsPaths(self):
        """Utility function to set important filepaths to scripts (manifest, js, css, html) for easy acess"""

        # Look into typical extension file names and then think about how to deal with annoying ones
        importantFiles = {
            'manifest': ['manifest.json'],
            'service_worker': ['service_worker.js'],
            'index': ['index.html']
        }

        # Loop through each item in important file dict.
        for attr_name, filenames in importantFiles.items():
            foundPath = None

            # Go through each file in list
            for fname in filenames:
                candidate = self.folderpath / fname
                # Check if path even exists
                if candidate.exists():
                    foundPath = candidate

            # If we found a path, then set self.attr to path
            if foundPath:
                setattr(self, attr_name, foundPath)
                print(f"Found {attr_name}")
            
            # Else not
            else:
                setattr(self, attr_name, None)
                print(f"Did not find {attr_name}")
                
        return

    def getManifestPath(self):
        """Utility function to return Extension's Manifest folder path"""
        return self.manifest
    
    def getIndexPath(self):
        """Utility function to return Extension's Index folder path"""
        return self.index
    
    def getServiceWorker(self):
        """Utility function to return Extension's Json folder path"""
        return self.service_worker