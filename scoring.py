import pandas as pd
from pathlib import Path
import joblib
from paths import * 

# All features with assigned weights from RF
feature_weights = {
    'avg_line_length': 0.07418,
    'specific_characters': 0.0649,
    'dynamic_code_gen_functions': 0.0621,
    'event_handlers': 0.05997,
    'DOM_operations': 0.0576,
    'keyword_density': 0.0516,
    'whitespace %': 0.05092,
    'DOM_change_sinks_density': 0.04959,
    'string_entropy': 0.04836,
    'word_size': 0.04577,
    'DOM_operations_density': 0.04402,
    'webRequestBlocking': 0.04185,
    'event_handlers_density': 0.03899,
    'num_external_urls': 0.03164,
    'DOM_change_sinks': 0.03122,
    'XMLHttpRequests_density': 0.02799,
    'num_script_tags': 0.0254,
    'num_script_src_attrs': 0.02437,
    'num_background_image': 0.02199,
    'storage': 0.0168,
    'All https domains': 0.01639,
    'XMLHttpRequests': 0.01254,
    'tabs': 0.00849,
    'webRequest': 0.00837,
    'modification_callbacks_density': 0.00833,
    'num_import_rules': 0.00792,
    'security_policy': 0.00759,
    'num_iframe_tags': 0.00612,
    'num_form_tags': 0.00582,
    'cookies': 0.0056,
    'num_external_iframe_src': 0.00464,
    'notifications': 0.0046,
    'num_http_urls': 0.00447,
    'modification_callbacks': 0.00422,
    'num_meta_refresh': 0.00422,
    'num_behavior': 0.00416,
    'management': 0.00394,
    'All http domains': 0.00358,
    'num_password_inputs': 0.00227,
    'num_external_script_src': 0.00215,
    'num_external_form_actions': 0.00185,
    'num_javascript_urls': 0.00121,
    'num_inline_event_handlers': 0.00121,
    'num_data_urls': 0.00083,
    'num_embed_tags': 0.00011,
    'num_object_tags': 8e-05,
    'HTTP_scripts_density': 1e-05,
    'HTTP_scripts': 0.0,
    'contextmenus': 0.0
}

# mal_csv = Path(r"C:\Users\frana\College_HW_Submissions\COMPS\fie-comps\ML\datasets\final_M.csv")
# benign_csv = Path(r"C:\Users\frana\College_HW_Submissions\COMPS\fie-comps\ML\datasets\final_B.csv")
# mal = pd.read_csv(mal_csv)
# benign = pd.read_csv(benign_csv)

def assign_scores(feature_df):
    rf_model = joblib.load(RF_ALL_FEATURES)
    rf_features = joblib.load(ALL_FEATURES)


    # Assigns a score based off the product of the raw counts and weights from RF
    for row in range(feature_df.shape[0]):
        prob = rf_model.predict_proba(feature_df[rf_features])[row][1]
        score = round(prob * 100, 2)
    
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