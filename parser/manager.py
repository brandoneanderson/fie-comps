import extension
from extractor import *
from manifest_parser import * 
from analyzer import *
from js_parser import *
from css_parser import *

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
        # WE HAVE TO RUN THROUGH THESE FILES AGAIN SO LETS SEE HOW WE CAN BEST OPTIMIZE PERFORMANCE
        for allfiles in (ext.js_files, ext.html_files, ext.json_files, ext.css_files):
            for file in allfiles:
                extractURLs(file, ext)
                if file.suffix == '.js':
                    analyzeJS(file, ext)
                if file.suffix == ".json":
                    continue
                if file.suffix == ".css":
                    analyze_CSS(file, ext)

    # Prep score dictionary:
    extensions_predictions = {key: None for key in extensions.keys()}

    # Analze and predict each extension!
    for name, ext in extensions.items():
        prediction = Score_Report(ext)
        prediction.predict()
        extensions_predictions[ext.getName()] = prediction.PREDICTION
        print(extensions_predictions)
