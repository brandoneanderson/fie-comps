import zipfile, manifest_parser
from pathlib import Path

"""
    Method to extract a compressed file according to its file type
    Input: Filename
    Output: Returns a folder in 'Extensions' with unpacked material
"""
def extractExtension(filename_og):
    script_dir = Path(__file__).parent

    # Grab local path to extension
    filename = Path('Extensions\\'+filename_og)
    if not filename.exists():
            print("File does not exist or is not supported. Sorry.\n")
            return

    # Create destination folder, will be in extensions
    destination_folder_name = filename_og.replace(filename.suffix, '')
    destination = script_dir/"Extensions"/destination_folder_name
    destination.mkdir(exist_ok=True)

    # Rename filename to .zip due to no proper .crx library to unpack file type
    if filename.suffix == '.crx':
        print("Omg a crx file, change it to a zip lmao\n")
        return
    
    # Unpack zip file
    if filename.suffix == '.zip':
        with zipfile.ZipFile(filename, 'r') as zip_ref:
            zip_ref.extractall(destination) 

        print("Woah, a zip cool. Content in 'Extension' folder!\n")   
        return
    
    # Unsupported file
    else:
        print("File does not exist or is not supported. Sorry.\n")
        return

"""
    Calls extract extension, short function to call in other files
    Input: None
    Output: None
"""
def exctract():
    filename = str(input("Please enter the file name: "))
    extractExtension(filename)
    return