from parser.extension import Extension
from parser.extractor import *
from parser.Scanners.manifest_parser import * 
from parser.analyzer import *
from parser.Scanners.js_parser import *
from parser.Scanners.css_parser import *
from parser.Scanners.html_parser import *
from ML.vectorize import *


## DEBUGGING CONFIG
# UPDATE AS NEEDED
TESTING_ML = 0
'''
    Core file for all parsers
'''

if __name__ == "__main__":

    # TESTING WIP-ML FUNCTIONS, WILL BE ADDED TO EOF
    if TESTING_ML:
        # test()
        yes = 0
    else:
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
        # for file in filesFound:
        #     folderPath = extractExtension(file)
        #     ext = extension.Extension(folderPath)
        #     ext.setScriptsPaths()
        #     extensions[ext.getName()] = ext
        for file in filesFound:
            folderPath = extractExtension(file)

            # skip if extraction failed
            if not folderPath:
                print(f"[WARN] Skipping extension (extract failed): {file}")
                continue

            ext = Extension(folderPath)
            ext.setScriptsPaths()
            extensions[ext.getName()] = ext

        # Parse through each extension and collect info
        for name, ext in extensions.items():
            manifest_path = ext.getManifestPath()

            if not manifest_path:
                print(f"[WARN] No manifest found for: {name} (folder={getattr(ext, 'path', None)}) — skipping")
                continue

            try:
                analyzeManifest(manifest_path, ext)
            except Exception as e:
                print(f"[WARN] Failed to analyze manifest for {name}: {e}")
                continue
            
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
                    if file.suffix == ".html":
                        analyze_HTML(file, ext)

        # Prep score dictionary:
        extensions_predictions = {key: None for key in extensions.keys()}

        # Analze and predict each extension!
        for name, ext in extensions.items():
            ext.setFinalJSTotals()
            prediction = Score_Report(ext)
            prediction.predict()
            extensions_predictions[ext.getName()] = prediction.PREDICTION
            # print("\n", ext.name, "\n", " JS Features:", ext.js_features, "\n CSS Features", ext.css_features, "\n HTML Features", ext.html_features, "\n")
        
        # ML vectorize
        setExtML(extensions)
        
        # print(extensions_predictions)
