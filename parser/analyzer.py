import extension

'''
    File to run all analysis on everything parsers collected and stored into extensions
    Will SCORE and determine whether extension class is malicious, suspicious, or benign
'''
SCORE = 0
MALICIOUS_THRESHOLD = 10
SUSPICIOUS_THRESHOLD = 5
PREDICTION = None
POSSIBLE_PREDICTION_LABELS = ['SAFE', 'MALICIOUS', 'LIKELY MALICIOUS']


def analyze(extension):
    SCORE = 0
    # Grab necessary info from extensions to run analysis & prediction
    permissions = extension.getPermissions()

    if 'tabs' in permissions:
        SCORE += 5

    if SCORE < SUSPICIOUS_THRESHOLD:
        PREDICTION = POSSIBLE_PREDICTION_LABELS[0]
    elif SCORE >= MALICIOUS_THRESHOLD:
        PREDICTION = POSSIBLE_PREDICTION_LABELS[1]
    else:
        PREDICTION = POSSIBLE_PREDICTION_LABELS[2]

    return PREDICTION