# import math

# def clamp(x: float, lo: float, hi: float) -> float:
#     return max(lo, min(hi, x))

# def risk_score_simple(prob_mal: float) -> int:
#     """0..1 -> 0..100"""
#     prob_mal = clamp(prob_mal, 0.0, 1.0)
#     return int(round(100.0 * prob_mal))

# def risk_score_thresholded(prob_mal: float, threshold: float) -> int:
#     """
#     Map probability to 0..100 such that threshold ~ 50.
#     Below threshold: 0..49, above threshold: 50..100.
#     """
#     prob_mal = clamp(prob_mal, 0.0, 1.0)
#     threshold = clamp(threshold, 1e-6, 1.0 - 1e-6)

#     if prob_mal < threshold:
#         # scale [0, threshold] -> [0, 49]
#         score = 49.0 * (prob_mal / threshold)
#     else:
#         # scale [threshold, 1] -> [50, 100]
#         score = 50.0 + 50.0 * ((prob_mal - threshold) / (1.0 - threshold))

#     return int(round(clamp(score, 0.0, 100.0)))

# def risk_level(score_0_100: int) -> str:
#     if score_0_100 >= 80:
#         return "CRITICAL"
#     if score_0_100 >= 50:
#         return "HIGH"
#     if score_0_100 >= 20:
#         return "MEDIUM"
#     return "LOW"

# def recommended_action(level: str) -> str:
#     return {
#         "LOW": "Allow",
#         "MEDIUM": "Review permissions & external requests",
#         "HIGH": "Warn user / require review",
#         "CRITICAL": "Block / quarantine extension",
#     }[level]

# def confidence_from_margin(prob_mal: float, threshold: float) -> str:
#     """
#     Rough confidence based on distance from threshold.
#     Not statistical confidence—just UX guidance.
#     """
#     d = abs(prob_mal - threshold)
#     if d >= 0.30:
#         return "HIGH"
#     if d >= 0.15:
#         return "MEDIUM"
#     return "LOW"
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
    if score >= 80:
        return "CRITICAL"
    if score >= 50:
        return "HIGH"
    if score >= 20:
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
