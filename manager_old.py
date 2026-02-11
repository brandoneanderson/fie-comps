# SCANNER COMPONENTS
from parser.extension import Extension
from parser.extractor import *
from parser.analyzer import *

# SCANNER PARSERS
from parser.Scanners.manifest_parser import * 
from parser.Scanners.js_parser import *
from parser.Scanners.css_parser import *
from parser.Scanners.html_parser import *

# ML MATERIALS / PATHS
from ML.vectorize import *
from ML.download_ext import *
from parser.paths import *
import pandas as pd


## DEBUGGING CONFIG
# UPDATE AS NEEDED
TESTING_ML = 0
DELETE_FILES = 1

'''
    Old core file to run our scanner.
    Really helpful for debugging and scanning multiple extensions at once
'''

if __name__ == "__main__":

    # TESTING WIP-ML FUNCTIONS, WILL BE ADDED TO EOF
    if TESTING_ML:
        # test()
        yes = 0
    else:
        # Grab csv of all benign ext IDs
        benign_ext_csv_df = pd.read_csv(MAL_EXT_CSV)

        ## ONLY DO BATCHES OF 200
        # 1200, SO 6 BATCHES
        for ext_id in benign_ext_csv_df["ID"][200:500]:
            download_crx(ext_id)
        

        # TESTING DOWNLOAD CRX FUNCTIONS
        # mybib_id = "phidhnmbkbkbkbknhldmpmnacgicphkf"
        # download_crx(mybib_id)

        # For easy testing
        folderName = 'Extensions'
        filesFound = searchFolder(folderName)

        # Dictionary to store extensions
        extensions = {}
        extensions_predictions = {}

        for file in filesFound:
            ext_paths = []

            try:
                ext_paths.append(file)
                folderPath = extractExtension(file)

                if not folderPath:
                    print(f"[WARN] Extraction failed: {file}")
                    continue

                ext_paths.append(folderPath)

                ext = Extension(folderPath)
                ext.setScriptsPaths()
                extensions[ext.getName()] = ext

            except Exception as e:
                print(f"[ERROR] Failed loading extension {file}: {e}")

            finally:
                if DELETE_FILES and folderPath is None:
                    for p in ext_paths:
                        delete_file(p)

        # Parse through each extension and collect info
        for name, ext in extensions.items():
            ext_paths = []

            try:
                # track extension folder
                ext_paths.append(ext.folderpath)
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
            except Exception as e:
                print(f"[Error] Extension failed: {name} -> {e}")
            
            finally:
                if DELETE_FILES:
                    for p in ext_paths:
                        delete_file(p)

        # Prep score dictionary:
        extensions_predictions = {key: None for key in extensions.keys()}

        # Analze and predict each extension!
        for name, ext in extensions.items():
            ext.setFinalValues()
            prediction = Score_Report(ext)
            prediction.predict()
            extensions_predictions[ext.getName()] = prediction.PREDICTION
        
        # ML vectorize
        setExtML(extensions)
        
        # print(extensions_predictions)
