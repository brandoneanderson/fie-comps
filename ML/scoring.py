
def clamp(x, lo, hi):
    return max(lo, min(hi, x))

def risk_score_thresholded(prob, threshold):
    prob = clamp(float(prob), 0.0, 1.0)
    threshold = clamp(float(threshold), 1e-6, 1.0 - 1e-6)

    if prob < threshold:
        score = 49.0 * (prob / threshold)
    else:
        score = 50.0 + 50.0 * ((prob - threshold) / (1.0 - threshold))

    return int(round(clamp(score, 0.0, 100.0)))

def risk_level(score):
    if score >= 35:
        return "CRITICAL"
    if score >= 20:
        return "HIGH"
    if score >= 10:
        return "MEDIUM"
    return "LOW"

def recommended_action(level):
    return {
        "LOW": "Allow",
        "MEDIUM": "Review permissions & network access",
        "HIGH": "Warn user / require review",
        "CRITICAL": "Block / quarantine",
    }[level]

def confidence_from_margin(prob, threshold):
    d = abs(float(prob) - float(threshold))
    if d >= 0.30:
        return "HIGH"
    if d >= 0.15:
        return "MEDIUM"
    return "LOW"
