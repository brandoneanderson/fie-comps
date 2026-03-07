import pandas as pd
from pathlib import Path
import joblib
from paths import * 

# All features with assigned weights from RF
feature_weights = {
    "avg_line_length": 0.07537840005501965,
    "specific_characters": 0.06468962237198636,
    "dynamic_code_gen_functions": 0.062434455563518086,
    "event_handlers": 0.06005200325763919,
    "DOM_operations": 0.0571701531275433,
    "keyword_density": 0.05181312129357617,
    "whitespace %": 0.04980281897150245,
    "DOM_change_sinks_density": 0.04882143862492233,
    "string_entropy": 0.04839810469294324,
    "word_size": 0.04513663977866575,
    "DOM_operations_density": 0.04379333779313552,
    "webRequestBlocking": 0.0419343739003661,
    "event_handlers_density": 0.038703980195342096,
    "DOM_change_sinks": 0.032021974207886016,
    "num_external_urls": 0.03188772772861642,
    "XMLHttpRequests_density": 0.028567850832624392,
    "num_script_tags": 0.02562613953516307,
    "num_script_src_attrs": 0.024485900869365064,
    "num_background_image": 0.02153463010319097,
    "storage": 0.016766569532747775,
    "All https domains": 0.016684576802392197,
    "XMLHttpRequests": 0.012401419762145992,
    "num_import_rules": 0.00860598233281345,
    "tabs": 0.008504731495115207,
    "webRequest": 0.008288956699352314,
    "modification_callbacks_density": 0.007976314961725517,
    "security_policy": 0.00736972298447148,
    "num_iframe_tags": 0.006080639051887923,
    "num_form_tags": 0.005876525111550299,
    "cookies": 0.005722942354630222,
    "notifications": 0.004658015126307566,
    "num_http_urls": 0.0045484463533580835,
    "num_external_iframe_src": 0.004333631073463373,
    "modification_callbacks": 0.004321919067535457,
    "num_password_inputs": 0.004169190652987695,
    "num_behavior": 0.004089952326059589,
    "management": 0.004064041941036509,
    "All http domains": 0.0034278251544732482,
    "num_inline_event_handlers": 0.0022097241262601657,
    "num_external_script_src": 0.0021476427059950046,
    "num_external_form_actions": 0.0019498251627816155,
    "num_meta_refresh": 0.00128930925123973,
    "num_javascript_urls": 0.00124389292689671,
    "num_data_urls": 0.0008296017328972642,
    "num_embed_tags": 0.00010374649986086999,
    "num_object_tags": 7.53051834615137e-05,
    "HTTP_scripts_density": 3.612886284850867e-06,
    "HTTP_scripts": 3.2638372621515404e-06,
    "contextmenus": 0.0
}

# mal_csv = Path(r"C:\Users\frana\College_HW_Submissions\COMPS\fie-comps\FINAL2_M.csv")
# benign_csv = Path(r"C:\Users\frana\College_HW_Submissions\COMPS\fie-comps\FINAL2_B.csv")
# mal = pd.read_csv(mal_csv)
# benign = pd.read_csv(benign_csv)

def assign_scores(feature_df):
    rf_model = joblib.load(RF_ALL_FEATURES)
    rf_features = rf_model.feature_names_in_

    stuff = {"0-10":0, "10-20":0, "20-30":0, "30-40":0,"40-50":0,"50-60":0,"60-70":0,"70-80":0,"80-90":0,"90-100":0}

     # Ensure all required RF features exist
    for col in rf_features:
        if col not in feature_df.columns:
            feature_df[col] = 0.0

    X_rf = feature_df.reindex(columns=rf_features).apply(pd.to_numeric, errors="coerce").fillna(0.0)
    # Assigns a score based off the product of the raw counts and weights from RF
    for row in range(feature_df.shape[0]):
        prob = rf_model.predict_proba(X_rf)[row][1]
        score = round(prob * 100, 2)
        if score <= 10:
            stuff["0-10"] += 1
        elif score > 10 and score <= 20:
            stuff["10-20"] += 1
        elif score > 20 and score <= 30:
            stuff["20-30"] += 1
        elif score > 30 and score <= 40:
            stuff["30-40"] += 1
        elif score > 40 and score <= 50:
            stuff["40-50"] += 1
        elif score > 50 and score <= 60:
            stuff["50-60"] += 1
        elif score > 60 and score <= 70:
            stuff["60-70"] += 1
        elif score > 70 and score <= 80:
            stuff["70-80"] += 1
        elif score > 80 and score <= 90:
            stuff["80-90"] += 1
        else:
            stuff["90-100"] += 1

    print(stuff)

    return score

# def clamp(x, lo, hi):
#     return max(lo, min(hi, x))

# def risk_score_thresholded(prob, threshold):
#     prob = clamp(float(prob), 0.0, 1.0)
#     threshold = clamp(float(threshold), 1e-6, 1.0 - 1e-6)

#     if prob < threshold:
#         score = 49.0 * (prob / threshold)
#     else:
#         score = 50.0 + 50.0 * ((prob - threshold) / (1.0 - threshold))

#     return int(round(clamp(score, 0.0, 100.0)))

def risk_level(score):
    if score >= 80:
        return "CRITICAL"
    elif score >= 50:
        return "HIGH"
    elif score >= 30:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    return "SAFE"

def recommended_action(level):
    return {
        "SAFE": "Safe for now, but be aware of future updates",
        "LOW": "Review permissions & network access",
        "MEDIUM": "Review permissions and consider removing if unsure",
        "HIGH": "Remove when you’re not using it",
        "CRITICAL": "Block / quarantine"
    }[level]


# if __name__ == "__main__":
#     assign_scores(benign)
#     assign_scores(mal)