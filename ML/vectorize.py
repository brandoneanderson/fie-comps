import pandas as pd

from parser.extension import Extension
from pathlib import Path

# TESTING Purposes
# Example extension creation

# bad_extension_path = Path(r"C:\Users\frana\College_HW_Submissions\COMPS\fie-comps\parser\Extensions\BadExtension")
# test_ext = Extension(bad_extension_path)

# test_ext.setScriptsPaths()
# test_ext.js_features = {'dynamic_code_gen_functions': 4, 'whitespace %': 0.19899964272954626, 'avg_line_length': 10.814345991561181, 'specific_characters': 0.28188638799571275, 'word_size': 5.696969696969697, 'string_entropy': 3.301374859754258, 'DOM_change_methods': 6, 'event_handlers': 2, 'HTTP_scripts': 1, 'modification_callbacks': 2, 'XMLHttpRequests': 1, 'keyword_density': 0.1038961038961039}
# test_ext.css_features = {'num_background_image': 1, 'num_behavior': 0, 'num_import_rules': 10, 'num_external_urls': 164}
# test_ext.html_features = {'num_script_tags': 8, 'num_script_src_attrs': 8, 'num_external_urls': 16}

def vectorizeExt(extension : Extension):
    # Grab all features & metadata info
    js_features = extension.js_features # dict
    css_features = extension.css_features # dict
    html_features = extension.html_features # dict
    permissions = extension.permissions # dict

    all_features = {}

    all_features.update(permissions)
    all_features.update(js_features)
    all_features.update(css_features)
    all_features.update(html_features)
    name = extension.name
    
    all_features["Extension Name"] = name

    return all_features

def add_extension(rows, ext:Extension):
    row = vectorizeExt(ext)
    rows.append(row)

def setExtML(set_exts):
    rows = []
    for name, ext in set_exts.items():
        add_extension(rows, ext)

    df = pd.DataFrame(rows)
    df.to_csv('outputM50_200.csv', index=False)
    print(df.shape)

def test():
    # test_dict = {"test":test_ext}
    # setExtML(test_dict)
    return