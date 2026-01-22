import extension
from extractor import *
from manifest_parser import * 
from analyzer import *

'''
    Core file for all parsers
'''

if __name__ == "__main__":
    # Search for all extension files

    # CLI to actually start running program, think about how to automate later on
    # I guess just download all extensions into 'Extensions' folder and leave that as folderName?
    #folderName = input("Please enter name of folder where you have extensions: ")

    # For easy testing
    folderName = 'Extensions'
    filesFound = searchFolder(folderName)

    # Dictionary to store extensions
    extensions = {}
    extensions_predictions = {}

    # Unpack every extension found, and create extension class for each ext
    for file in filesFound:
        folderPath = extractExtension(file)
        ext = extension.Extension(folderPath)
        ext.setScriptsPaths()
        extensions[ext.getName()] = ext

    # Parse through each extension and collect info
    for name, ext in extensions.items():
        analyzeManifest(ext.getManifestPath(), ext)

    # Prep score dictionary:
    extensions_predictions = {key: None for key in extensions.keys()}

    # Analze and predict each extension!
    for name, ext in extensions.items():
        prediction = analyze(ext)
        extensions_predictions[ext.getName()] = prediction

    print(extensions_predictions)
