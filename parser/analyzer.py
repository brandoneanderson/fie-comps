from extractor import *

'''
    File to run all analysis on everything parsers collected and stored into extensions
    Will SCORE and determine whether extension class is malicious, suspicious, or benign
'''

class Score_Report:
    def __init__(self, extensionClass):
        
        # Record refernce to extension Class instance
        self.extension = extensionClass

        # SCORING THRESHOLDS & VALUES
        self.MALICIOUS_THRESHOLD = 10
        self.SUSPICIOUS_THRESHOLD = 5
        self.PREDICTION = None
        self.POSSIBLE_PREDICTION_LABELS = ['SAFE', 'MALICIOUS', 'LIKELY MALICIOUS']
        self.PERMISSISION_MULTIPLIER = 0.4
        self.score = 0
        self.permission_count = 0

        # COMMON MALICIOUS FEATURES
        # ^ DATA ACQUIRED FROM 'A Combined Static and Dynamic Analysis Approach to Detect Malicious Browser Extensions'
        self.TOP_MALICIOUS_BEHAVIORS = ['tabs', '<all_urls>', 'http://*/*', '"https://*/*"', '://*/*', 'webRequest', 'webRequestBlocking', 'storage', 'notifications', 'cookies', 'management', 'contextMenus']

    def predict(self):
        # Grab necessary info from extensions to run analysis & prediction
        self.analyzePermissions()

        self.scoreExtension()
        if self.score < self.SUSPICIOUS_THRESHOLD:
            self.PREDICTION = self.POSSIBLE_PREDICTION_LABELS[0]
        elif self.score >= self.MALICIOUS_THRESHOLD:
            self.PREDICTION = self.POSSIBLE_PREDICTION_LABELS[1]
        else:
            self.PREDICTION = self.POSSIBLE_PREDICTION_LABELS[2]
        
        return

    def scoreExtension(self):
        self.score = self.permission_count * self.PERMISSISION_MULTIPLIER
    
    def analyzePermissions(self):
        permissions = self.extension.getPermissions()
        permissions.extend(self.extension.host_permissions)

        for permission in permissions:
            if permission in self.TOP_MALICIOUS_BEHAVIORS:
                self.permission_count += 1