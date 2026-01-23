import zipfile, re
from pathlib import Path



def extractExtension(filepath):
    """
    Method to extract a compressed file according to its file type
    Input: Path type where file is located
    Output: Returns name of file extracted, but a folder is created in 'Extensions' with unpacked material and name of extension as folder name
    """

    if not filepath.exists():
            raise FileNotFoundError(filepath)

    # Grab name of file, and remove .zip/.crx/etc.
    filename = str(Path(filepath.name).stem)

    # Create destination for extraction deposit
    # filepath.parent = '.../Extensions'
    destination = filepath.parent/filename

    # Avoid re-extraction if already prev. done
    if destination.exists():
        print("File was already extracted! Name:", filename)
        return destination

    # Make directory/folder if not existsing already
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

def extractURLs(file, extClass):
    '''Given Path to file, reads the file and extracts all urls found within. Don't think it works with obfuscated urls'''
    # Attempt to read the file
    try:
        with open(file, 'r', encoding='utf8') as fileloaded:
            # grab entire script and store it as string
            content = fileloaded.read()

            # TESTING TO SEE FUNCTIONALITY NOT FINAL; CREDIT TO EXTANALYSIS ON GITHUB
            curls = re.findall('(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?', content)
            for url in curls:
                urlresult = {"file":file, "url":url[0]+'://'+url[1]+url[2]}
                if urlresult not in extClass.urls:
                    extClass.urls.append(urlresult)
            # TESTING TO SEE FUNCTIONALITY NOT FINAL; CREDIT TO EXTANALYSIS ON GITHUB
            
    
    # Throw appropriate errors if anything goes wrong while attempting to read file
    except FileNotFoundError:
        print(f"Error: The file {file} was not found.")
    except Exception as e:
        print(f"An error ocurred: {e}")