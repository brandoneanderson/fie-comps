# from selenium import webdriver
# from selenium.webdriver.common.by import By
import re

def analyze_CSS(cssFile, extClass):
    with open(cssFile, 'r', encoding='utf-8') as file:
        css = file.read()

    features = {
        # CSS Features that may exhibit malicious behavior

        # Malicious images could be injected into background properties
        "num_background_image": r"background-image\s*:",

        # Possible to inject malicious codes into stylesheets via behavior property
        "num_behavior": r"behavior\s*:",

        # Attackers could execute any codes or cause a DoS through import rules in a stylesheet
        "num_import_rules": r"@import\b",

        # external resource loading 
        "num_external_urls": r"url\s*\(",
    }

    results = {}

    # For each feature in the features dict, go through them and count all instances of each feature
    for name, pattern in features.items():
        results[name] = len(re.findall(pattern, css, re.IGNORECASE))

    # If first css file parsed, then assign results
    if extClass.css_features  == None:
        extClass.css_features = results

    # Update dictionary to sum up total freq of features found across all css files
    else:
        for feature, count in extClass.css_features.items():
            extClass.css_features[feature] += results[feature]
    return