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
from ML.download_mal_ext import *
import pandas as pd


## DEBUGGING CONFIG
# UPDATE AS NEEDED
TESTING_ML = 0
DELETE_FILES = 1

'''
    Old core file to run our scanner.
    Really helpful for debugging and scanning multiple extensions at once
'''

def Scan_Extension(id):

    # # Grab csv of all benign ext IDs
    # benign_ext_csv_df = pd.read_csv(BENIGN_EXT_CSV)
    # malicious_ext = pd.read_csv(MAL_CHROME_STATS_CSV)

    # for ext_id in malicious_ext["ID"][0:1]:
    #     download_crx(ext_id)

    # for id, version in zip(malicious_ext['id'][0:2], malicious_ext['version'][0:2]):
    #     download_mal_ext(id, version)
    

    # TESTING DOWNLOAD CRX FUNCTIONS
    # mybib_id = "phidhnmbkbkbkbknhldmpmnacgicphkf"
    download_crx(id)

    # For easy testing
    folderName = 'Extensions'
    filesFound = searchFolder(folderName)

    # Dictionary to store extensions
    extensions = {}
    extensions_predictions = {}

    # Loop through each file, and extract the ext and set script paths
    for file in filesFound:
        try:
            folderPath = extractExtension(file)

            if not folderPath:
                print(f"[WARN] Extraction failed: {file}")
                continue

            ext = Extension(folderPath)
            ext.setScriptsPaths()
            extensions[ext.getName()] = ext

        except Exception as e:
            print(f"[ERROR] Failed loading extension {file}: {e}")
        
        finally:
            delete_file(file)

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
            
            # Extract features from each relevant file
            for allfiles in (ext.js_files, ext.html_files, ext.json_files, ext.css_files):
                for file in allfiles:
                    # extractURLs(file, ext)
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

    # Set final values for all features gathered
    for name, ext in extensions.items():
        ext.setFinalValues()
    
    # ML vectorize
    df_ext = setExtML(extensions)
    
    return df_ext
