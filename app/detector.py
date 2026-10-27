import os
import re
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Load ML artifacts
vectorizer_path = os.path.join(MODELS_DIR, "vectorizer.pkl")
classifier_path = os.path.join(MODELS_DIR, "classifier.pkl")

clf = None
vec = None

try:
    if os.path.exists(vectorizer_path) and os.path.exists(classifier_path):
        with open(vectorizer_path, "rb") as f:
            vec = pickle.load(f)
        with open(classifier_path, "rb") as f:
            clf = pickle.load(f)
except Exception as e:
    print(f"Warning: Failed to load ML model: {e}")

# Scam keyword categories & weights
SCAM_INDICATORS = {
    "financial_demands": {
        "title": "Monetary / Fee Demands",
        "weight": 35,
        "keywords": [
            "registration fee", "security deposit", "refundable deposit", "processing fee",
            "laptop charges", "gate pass", "id card fee", "training fee", "courier charges",
            "pay upfront", "document verification fee", "kit charges", "setup fee",
            "pay to receive", "deposit money", "crypto", "bitcoin", "usdt", "gift card",
            "apple gift card", "steam wallet", "paytm payment", "phonepe", "gpay screenshot"
        ]
    },
    "suspicious_channels": {
        "title": "Dubious Communication Channels",
        "weight": 25,
        "keywords": [
            "telegram", "t.me/", "@", "whatsapp only", "message on whatsapp", "no interview",
            "direct joining", "direct appointment letter", "without interview", "no test",
            "immediate offer letter", "send aadhar", "send bank details"
        ]
    },
    "task_scams": {
        "title": "Task & Rating Fraud Patterns",
        "weight": 25,
        "keywords": [
            "youtube video like", "like youtube", "rate hotels", "hotel rating", "google map rating",
            "data entry typing", "copy paste", "sms sending", "captcha solver", "earn daily",
            "daily payout", "30 minutes work", "work 1 hour", "guaranteed income"
        ]
    },
    "unrealistic_claims": {
        "title": "Unrealistic Promises & Urgency",
        "weight": 15,
        "keywords": [
            "urgent hiring", "limited seats", "hurry limited", "100% genuine guaranteed",
            "earn 50,000", "earn 80,000", "earn 90,000", "earn 1,20,000", "no skills needed",
            "no experience required earn"
        ]
    }
}

GENUINE_INDICATORS = [
    "coding round", "technical assessment", "git", "github", "github profile", "portfolio",
    "pre-placement offer", "ppo", "drf", "django", "react", "react.js", "docker", "kubernetes",
    "unit test", "code review", "relational database", "postgresql", "sql", "aws", "azure",
    "google meet", "proctored", "official careers portal", "equal opportunity employer",
    "no fees required", "stipend: competitive", "mentorship"
]

FREE_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "rediffmail.com"]

def analyze_job(job_details: dict) -> dict:
    """
    Perform deep hybrid scam analysis on job posting details using
    Natural Language Processing, Trained ML Classifier, and Heuristic Rules.
    """
    text_content = (
        f"{job_details.get('title', '')} "
        f"{job_details.get('company', '')} "
        f"{job_details.get('salary', '')} "
        f"{job_details.get('description', '')} "
        f"{' '.join(job_details.get('contact_emails', []))} "
        f"{' '.join(job_details.get('telegram_links', []))} "
        f"{' '.join(job_details.get('whatsapp_links', []))}"
    ).strip()

    lower_text = text_content.lower()

    # 1. Run Machine Learning Classifier
    ml_scam_prob = 0.0
    if clf and vec and len(text_content) > 10:
        try:
            vec_input = vec.transform([text_content])
            probs = clf.predict_proba(vec_input)[0]
            ml_scam_prob = float(probs[1]) # probability of class 1 (Scam)
        except Exception as e:
            ml_scam_prob = 0.5
    else:
        ml_scam_prob = 0.5

    # 2. Heuristic Rule Analysis
    category_matches = {}
    matched_red_flags = []
    
    financial_score = 0
    communication_score = 0
    task_risk_score = 0
    urgency_risk_score = 0

    for cat_key, cat_data in SCAM_INDICATORS.items():
        matched_in_cat = []
        for kw in cat_data["keywords"]:
            if kw in lower_text:
                matched_in_cat.append(kw)
                # Find contextual snippet
                idx = lower_text.find(kw)
                start = max(0, idx - 40)
                end = min(len(text_content), idx + len(kw) + 40)
                snippet = "..." + text_content[start:end].strip() + "..."
                matched_red_flags.append({
                    "keyword": kw,
                    "category": cat_data["title"],
                    "context": snippet
                })
        
        category_matches[cat_key] = matched_in_cat

    # Calculate subdimension risks
    if len(category_matches["financial_demands"]) > 0:
        financial_score = min(100, 35 + len(category_matches["financial_demands"]) * 25)
    
    # Check for free email used by corporate employer
    email_risk = False
    for email in job_details.get("contact_emails", []):
        domain = email.split("@")[-1].lower() if "@" in email else ""
        if domain in FREE_EMAIL_DOMAINS:
            email_risk = True
            matched_red_flags.append({
                "keyword": f"Free Email ({email})",
                "category": "Dubious Communication Channels",
                "context": f"Corporate/Official recruiter using free public domain: {email}"
            })
            break

    if len(job_details.get("telegram_links", [])) > 0 or len(category_matches["suspicious_channels"]) > 0 or email_risk:
        communication_score = min(100, 30 + (len(category_matches["suspicious_channels"]) + (2 if email_risk else 0)) * 20)

    if len(category_matches["task_scams"]) > 0:
        task_risk_score = min(100, 40 + len(category_matches["task_scams"]) * 25)

    if len(category_matches["unrealistic_claims"]) > 0:
        urgency_risk_score = min(100, 25 + len(category_matches["unrealistic_claims"]) * 20)

    # Genuine indicators check
    detected_genuine = []
    for gi in GENUINE_INDICATORS:
        if gi in lower_text:
            detected_genuine.append(gi)

    # Heuristic aggregate score
    heuristic_total = (
        (financial_score * 0.40) +
        (communication_score * 0.30) +
        (task_risk_score * 0.20) +
        (urgency_risk_score * 0.10)
    )

    # Mitigate with genuine indicators (if legitimate company signs are present and no financial demand)
    if len(detected_genuine) > 0 and len(category_matches["financial_demands"]) == 0:
        mitigation = min(40, len(detected_genuine) * 10)
        heuristic_total = max(0, heuristic_total - mitigation)

    # Combined Scam Probability
    # 50% ML Model + 50% Heuristics (or high clamp if direct payment scam detected)
    combined_score = (ml_scam_prob * 100 * 0.45) + (heuristic_total * 0.55)
    
    # Override: If money/fee demand or telegram task scam is explicitly found, it is almost certainly a scam!
    if len(category_matches["financial_demands"]) >= 1:
        combined_score = max(combined_score, 85.0)
    if "telegram" in lower_text and ("task" in lower_text or "daily payout" in lower_text or "fee" in lower_text):
        combined_score = max(combined_score, 90.0)

    combined_score = min(99.0, max(1.0, combined_score))
    scam_score_round = round(combined_score, 1)

    # Categorization
    if scam_score_round < 25.0:
        verdict = "GENUINE / SAFE"
        verdict_class = "success"
        verdict_desc = "This job posting displays hallmarks of an authentic corporate position with structured requirements, standard processes, and no fee requests."
    elif scam_score_round < 60.0:
        verdict = "SUSPICIOUS / PROCEED WITH CAUTION"
        verdict_class = "warning"
        verdict_desc = "This posting displays some warning signs (vague details, unusual communication channels, or elevated promises). Verify thoroughly before applying."
    else:
        verdict = "LIKELY FAKE / SCAM"
        verdict_class = "danger"
        verdict_desc = "High-confidence fraudulent listing detected! Multiple critical red flags found (monetary demands, suspicious communication, or typical task scam patterns)."

    # Safety checklist recommendations
    safety_tips = []
    if len(category_matches["financial_demands"]) > 0 or financial_score > 30:
        safety_tips.append("CRITICAL: Legitimate employers NEVER ask candidates for security deposits, laptop fees, training charges, or gate pass fees. NEVER transfer money.")
    if communication_score > 30 or email_risk:
        safety_tips.append("Professional HR teams conduct interviews via Google Meet, MS Teams, Zoom, or office visits—NOT solely over Telegram or WhatsApp chats.")
    if email_risk:
        safety_tips.append("Verify the recruiter's email domain. Reputable corporations recruit from @company.com domains, not personal @gmail or @yahoo addresses.")
    if task_risk_score > 30:
        safety_tips.append("Beware of 'like YouTube video' or 'hotel review' tasks. These are classic cyber fraud schemes designed to steal your money through prepaid recharge tasks.")
    
    if len(safety_tips) == 0:
        safety_tips.append("Always verify the company on official portals like the Ministry of Corporate Affairs (MCA) and LinkedIn.")
        safety_tips.append("Never share sensitive personal documents (OTP, Net Banking, Blank Cheques) during the application phase.")

    return {
        "scam_score": scam_score_round,
        "trust_score": round(100.0 - scam_score_round, 1),
        "verdict": verdict,
        "verdict_class": verdict_class,
        "verdict_desc": verdict_desc,
        "ml_probability": round(ml_scam_prob * 100, 1),
        "heuristic_score": round(heuristic_total, 1),
        "dimension_scores": {
            "financial_risk": round(financial_score),
            "communication_risk": round(communication_score),
            "task_scam_risk": round(task_risk_score),
            "urgency_risk": round(urgency_risk_score)
        },
        "red_flags": matched_red_flags,
        "genuine_indicators": detected_genuine,
        "safety_tips": safety_tips
    }
