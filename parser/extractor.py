import zipfile
from pathlib import Path



def extractExtension(filepath):
    """
    Method to extract a compressed file according to its file type
    Input: Path type where file is located
    Output: Returns name of file extracted, but a folder is created in 'Extensions' with unpacked material and name of extension as folder name
    """

    if not filepath.exists():
            print("File does not exist or is not supported. Sorry.\n")
            return

    # Grab name of file, and remove .zip/.crx/etc.
    filename = str(Path(filepath.name).stem)

    # Create destination for extraction deposit
    # filepath.parent = '.../Extensions'
    destination = filepath.parent/filename
    destination.mkdir(exist_ok=True)

    # Avoid re-extraction if already prev. done
    if destination.exists():
        print("File was already extracted! Name:", filename)
        return destination

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

    return destination
    
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