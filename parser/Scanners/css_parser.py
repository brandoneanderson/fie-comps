# from selenium import webdriver
# from selenium.webdriver.common.by import By
import re

def _cap_add(examples: dict, key: str, value: str, cap: int = 10):
    if not value:
        return
    bucket = examples.setdefault(key, [])
    if value in bucket:
        return
    if len(bucket) >= cap:
        return
    bucket.append(value)

def _ensure_css_fields(extClass):
    if extClass.css_features is None or not isinstance(extClass.css_features, dict):
        extClass.css_features = {}
    if not hasattr(extClass, "css_examples") or extClass.css_examples is None or not isinstance(extClass.css_examples, dict):
        extClass.css_examples = {}
    return extClass.css_features, extClass.css_examples


def analyze_CSS(cssFile, extClass):

    css_features, css_examples = _ensure_css_fields(extClass)

    with open(cssFile, 'r', encoding='utf-8') as file:
        css = file.read()

    features = {
        # CSS Features that may exhibit malicious behavior

        # Malicious images could be injected into background properties
        "num_background_image": r"background-image\s*:",

        # Possible to inject malicious codes into stylesheets via behavior property
        "num_behavior": r"\bbehavior\s*:",

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
    # if extClass.css_features  == None:
    #     extClass.css_features = results

    # # Update dictionary to sum up total freq of features found across all css files
    # else:
    #     for feature, count in results.items():
    #         extClass.css_features[feature] += count

     # collect example @import targets (up to 10)
    for m in re.finditer(r"@import\s+(?:url\()?['\"]?([^'\"\)\s;]+)", css, re.IGNORECASE):
        _cap_add(css_examples, "import_urls", m.group(1))

    # collect example url(...) targets (up to 10)
    for m in re.finditer(r"url\(\s*['\"]?([^'\"\)\s]+)\s*['\"]?\s*\)", css, re.IGNORECASE):
        _cap_add(css_examples, "resource_urls", m.group(1))

    # Merge counts robustly (works even if dict was overwritten)
    for k, v in results.items():
        css_features[k] = css_features.get(k, 0) + int(v)
    return