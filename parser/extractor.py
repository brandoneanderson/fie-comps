import zipfile
from pathlib import Path

class Extension:
    """
        Class to keep track of unpacked extension info such as names, folderpaths, and quick access to specific files
    """
    def __init__(self):
        self.filename = None
        self.folderpath = None
        self.manifestPath = None
        self.jsonPath = None
        self.indexPath = None

    def extractExtension(self, filepath):
        """
        Method to extract a compressed file according to its file type
        Input: Path type where file is located
        Output: Returns a folder in 'Extensions' with unpacked material and name of extension as folder name
        """

        if not filepath.exists():
                print("File does not exist or is not supported. Sorry.\n")
                return

        # Grab name of file, and remove .zip/.crx/etc.
        filename = str(Path(filepath.name).stem)
        self.filename = filename

        # Create destination for extraction deposit
        # filepath.parent = '.../Extensions'
        destination = filepath.parent/filename
        self.folderpath = destination
        destination.mkdir(exist_ok=True)

        # Rename filename to .zip due to no proper .crx library to unpack file type
        if filepath.suffix == '.crx':
            print("Omg a crx file, change it to a zip lmao\n")
        
        # Unpack zip file
        if filepath.suffix == '.zip':
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(destination) 

            print("Woah, a zip cool. Content in 'Extensions' folder!\n")   
        
        # Unsupported file
        else:
            print("File does not exist or is not supported. Sorry.\n")

        # Record important file paths
        self.setAppropriateFilePaths()
        return
    
    def getName(self):
        """Utility function to return Extension filename"""
        return self.filename
    
    def getFolderPath(self):
         """Utility function to return Extension folder path"""
         return self.folderpath
    
    def setAppropriateFilePaths(self):
        """Utility function to set important filepaths for easy acess"""
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
        return self.manifestPath
    
    def getIndexPath(self):
        """Utility function to return Extension's Index folder path"""
        return self.indexPath
    
    def getJsonPath(self):
        """Utility function to return Extension's Json folder path"""
        return self.jsonPath
    
def searchFolder(extensionFolderName):
    '''Given a folder name for where extensions are held, searches for extionsions within folder of type '.zip' and '.crx' '''
    # Grab local path where this .py script is found
    script_dir = Path(__file__).parent

    # Grab path to extensions folder
    extensionFolder = script_dir/extensionFolderName

    # Make sure path exists
    if not extensionFolder.exists():print("Extensions folder not located here: ", extensionFolder);return

    # Search for zip files!
    filesFound = list(Path.glob(extensionFolder, '*.zip'))

    for path in filesFound:
        print("We found the following file: ", path)
    
    return filesFound