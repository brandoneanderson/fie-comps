import extension
from extractor import *
from Scanners.manifest_parser import * 
from analyzer import *
from Scanners.js_parser import *
from Scanners.css_parser import *
from Scanners.html_parser import *

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
    # for file in filesFound:
    #     folderPath = extractExtension(file)
    #     ext = extension.Extension(folderPath)
    #     ext.setScriptsPaths()
    #     extensions[ext.getName()] = ext
    for file in filesFound:
        print(file)
        folderPath = extractExtension(file)

         # skip if extraction failed
        if not folderPath:
            print(f"[WARN] Skipping extension (extract failed): {file}")
            continue

        ext = extension.Extension(folderPath)
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
        print(ext.js_features)
        
    print(extensions_predictions)
