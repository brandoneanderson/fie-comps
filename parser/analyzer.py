from .extractor import *

'''
    File to run all analysis on everything parsers collected and stored into extensions
    Will SCORE and determine whether extension class is malicious, suspicious, or benign
'''

class Score_Report:
    def __init__(self, extensionClass):
        
        # Record refernce to extension Class instance
        self.extension = extensionClass
        self.score = 0
        self.permission_count = 0
        self.CSS_feature_count = 0

        self.HTML_feature_count = 0
        self.PREDICTION = {}
        self.POSSIBLE_PREDICTION_LABELS = ['SAFE', 'MALICIOUS', 'SUSPICIOUS']

        # SCORING THRESHOLDS
        self.MALICIOUS_THRESHOLD = 20
        self.SUSPICIOUS_THRESHOLD = 10

        # SCORING MULTIPLIERS - - - - - - - - DEF UPDATE WITH ACTUAL METHODOLOGY
        self.PERMISSISION_MULTIPLIER = 0.2
        self.CSS_FEATURE_MULTIPLIER = 0.06
        self.HTML_FEATURE_MULTIPLIER = 0.08

        self.HTML_FEATURE_WEIGHTS = {
            "num_inline_event_handlers": 2.0,     # onclick=, onload=...
            "num_javascript_urls": 3.0,           # javascript: in href/src
            "num_data_urls": 2.0,                # data: URLs (can hide payloads)
            "num_http_urls": 3.0,                # insecure transport
            "num_external_iframe_src": 2.0,
            "num_external_form_actions": 2.5,
            "num_external_script_src": 2.5,
            "num_meta_refresh": 1.5,
            "num_password_inputs": 2.0,
        }
        # COMMON MALICIOUS FEATURES
        # ^ DATA ACQUIRED FROM 'A Combined Static and Dynamic Analysis Approach to Detect Malicious Browser Extensions'
        self.TOP_MALICIOUS_BEHAVIORS = ['tabs', '<all_urls>', 'http://*/*', '"https://*/*"', '://*/*', 'webRequest', 'webRequestBlocking', 'storage', 'notifications', 'cookies', 'management', 'contextMenus']

    def predict(self):
        # Grab necessary info from extensions to run analysis & prediction
        self.analyzePermissions()
        self.analyzeFeatures()

        self.scoreExtension()
        if self.score < self.SUSPICIOUS_THRESHOLD:
            self.PREDICTION[self.POSSIBLE_PREDICTION_LABELS[0]] = "Score: " + str(self.score)
        elif self.score >= self.MALICIOUS_THRESHOLD:
            self.PREDICTION[self.POSSIBLE_PREDICTION_LABELS[1]] = "Score: " + str(self.score)
        else:
            self.PREDICTION[self.POSSIBLE_PREDICTION_LABELS[2]] = "Score: " + str(self.score)
        
        return

    def scoreExtension(self):
        self.score = (self.permission_count * self.PERMISSISION_MULTIPLIER) + (self.CSS_feature_count * self.CSS_FEATURE_MULTIPLIER)+ (self.HTML_feature_count * self.HTML_FEATURE_MULTIPLIER)
    
    def analyzePermissions(self):
        #permissions = self.extension.getPermissions()
        #permissions.extend(self.extension.host_permissions)
        # getPermissions() might return None
        permissions = list(self.extension.getPermissions() or [])

        # host_permissions might be None
        host_perms = list(getattr(self.extension, "host_permissions", None) or [])
        permissions.extend(host_perms)

        for permission in permissions:
            if permission in self.TOP_MALICIOUS_BEHAVIORS:
                self.permission_count += 1

    def analyzeFeatures(self):
        #CSS_features_data = self.extension.css_features
        # css_features might be None
        CSS_features_data = getattr(self.extension, "css_features", None) or {}
        self.CSS_feature_count = sum(CSS_features_data.values())
        # total_count = 0
        # for feature, count in CSS_features_data.items():
        #     total_count += count
        # self.CSS_feature_count = total_count
         # HTML features (weighted sum)
        HTML_features_data = getattr(self.extension, "html_features", None) or {}
        weighted_total = 0.0
        for feature, count in HTML_features_data.items():
            w = float(self.HTML_FEATURE_WEIGHTS.get(feature, 1.0))
            try:
                weighted_total += w * float(count)
            except Exception:
                # ignore weird non-numeric counts
                continue
        self.HTML_feature_count = weighted_total

