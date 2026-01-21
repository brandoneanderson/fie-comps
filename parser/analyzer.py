import extension
from extractor import *
from manifest_parser import * 

'''
    Core file for all parsers
'''

if __name__ == "__main__":
    # Search for all extension files
    #folderName = input("Please enter name of folder where you have extensions: ")

    # For easy testing
    folderName = 'Extensions'
    filesFound = searchFolder(folderName)

    # Dictionary to store extensions
    extensions = {}

    # Unpack every extension found
    for file in filesFound:
        folderPath = extractExtension(file)
        print("Folder path is: ", folderPath)
        ext = extension.Extension(folderPath)
        ext.setScriptsPaths()
        extensions[ext.getName()] = ext

    # Analyze each extension found!
    print('\n\n')
    for name, ext in extensions.items():
        analyzeManifest(ext.getManifestPath())
