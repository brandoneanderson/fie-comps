from extractor import *

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
        self.PREDICTION = {}
        self.POSSIBLE_PREDICTION_LABELS = ['SAFE', 'MALICIOUS', 'SUSPICIOUS']

        # SCORING THRESHOLDS
        self.MALICIOUS_THRESHOLD = 20
        self.SUSPICIOUS_THRESHOLD = 10

        # SCORING MULTIPLIERS - - - - - - - - DEF UPDATE WITH ACTUAL METHODOLOGY
        self.PERMISSISION_MULTIPLIER = 0.2
        self.CSS_FEATURE_MULTIPLIER = 0.06

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
        self.score = (self.permission_count * self.PERMISSISION_MULTIPLIER) + (self.CSS_feature_count * self.CSS_FEATURE_MULTIPLIER)
    
    def analyzePermissions(self):
        permissions = self.extension.getPermissions()
        permissions.extend(self.extension.host_permissions)

        for permission in permissions:
            if permission in self.TOP_MALICIOUS_BEHAVIORS:
                self.permission_count += 1

    def analyzeFeatures(self):
        CSS_features_data = self.extension.css_features
        total_count = 0
        for feature, count in CSS_features_data.items():
            total_count += count
        self.CSS_feature_count = total_count
        
