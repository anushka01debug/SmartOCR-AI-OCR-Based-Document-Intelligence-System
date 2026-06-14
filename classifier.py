import json
import os
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "settings.json")
DEFAULT_KEYWORDS = {
    "Invoice": [
        "invoice", "bill to", "due date", "subtotal", "tax", 
        "purchase order", "invoice number", "amount due", "remit to", "billing address"
    ],
    "Receipt": [
        "receipt", "total paid", "change due", "thank you", 
        "items", "cashier", "store #", "visa", "mastercard", "tendered", "payment method"
    ],
    "Certificate": [
        "certificate", "awarded", "hereby certify", "signature", 
        "presented to", "recognition of", "achievement", "this certificate", "successful completion"
    ],
    "Question Paper": [
        "marks", "question", "answer all", "section a", "section b", 
        "maximum marks", "duration:", "time allowed", "each question", "roll no"
    ],
    "Notes": [
        "chapter", "unit", "definition", "summary", "key points", 
        "introduction", "conclusion", "references", "lecture notes", "study guide", "important concepts"
    ]
}
def load_settings():
    """Loads settings from settings.json or initializes with defaults."""
    if not os.path.exists(SETTINGS_PATH):
        settings = {"keywords": DEFAULT_KEYWORDS}
        save_settings(settings)
        return settings
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # If read fails, return defaults
        return {"keywords": DEFAULT_KEYWORDS}
def save_settings(settings):
    """Saves settings dictionary to settings.json."""
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception:
        return False
def get_keywords():
    """Retrieves only the keywords dictionary."""
    return load_settings().get("keywords", DEFAULT_KEYWORDS)
def save_keywords(keywords):
    """Updates only the keywords in settings."""
    settings = load_settings()
    settings["keywords"] = keywords
    return save_settings(settings)
def classify_document(text: str):
    """
    Classifies a document based on text keyword scores.
    Returns:
      - best_label: str (The classified document category, e.g. "Invoice")
      - scores: dict (Raw matching frequency for each category)
    """
    t = text.lower()
    keywords = get_keywords()
    
    # Calculate scores (occurrences of each keyword in the lowercase text)
    scores = {}
    for label, kws in keywords.items():
        score = 0
        for kw in kws:
            # Count exact occurrences or simple presence
            # Using count gives weights to repeated occurrences (which is better for classification)
            score += t.count(kw.lower())
        scores[label] = score
        
    # Get best match
    best_label = "Unknown"
    top_score = 0
    
    if scores:
        best, top = max(scores.items(), key=lambda x: x[1])
        if top > 0:
            best_label = best
            top_score = top
            
    return best_label, scores
