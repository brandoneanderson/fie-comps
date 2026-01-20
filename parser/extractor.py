import zipfile, manifest_parser
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

    def extractExtension(self):
        """
        Method to extract a compressed file according to its file type
        Input: Filename
        Output: Returns a folder in 'Extensions' with unpacked material
        """

        filename_og = str(input("Please enter the file name: "))

        script_dir = Path(__file__).parent

        # Grab local path to extension
        filename = Path('Extensions\\'+filename_og)
        if not filename.exists():
                print("File does not exist or is not supported. Sorry.\n")
                return

        # Create destination folder, will be in extensions
        destination_folder_name = filename_og.replace(filename.suffix, '')
        self.filename = destination_folder_name
        destination = script_dir/"Extensions"/destination_folder_name
        self.folderpath = destination
        destination.mkdir(exist_ok=True)

        # Rename filename to .zip due to no proper .crx library to unpack file type
        if filename.suffix == '.crx':
            print("Omg a crx file, change it to a zip lmao\n")
        
        # Unpack zip file
        if filename.suffix == '.zip':
            with zipfile.ZipFile(filename, 'r') as zip_ref:
                zip_ref.extractall(destination) 

            print("Woah, a zip cool. Content in 'Extension' folder!\n")   
        
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
        self.manifestPath = Path(str(self.folderpath) + '\\manifest.json')
        self.jsonPath = Path(str(self.folderpath) + '\\service_worker.js')
        self.indexPath = Path(str(self.folderpath) + '\\index.html')
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