import re

class RuleBasedClassifier:
    def __init__(self):
        self.rules = {
            "fees": {
                "keywords": [r"\bcost\b", r"\bfee\b", r"\bfees\b", r"\bprice\b", r"\bpricing\b", r"\bpay\b", r"\bhow much\b"],
                "intent": "fees",
                "stage": "Contacted",
                "reply": "Our course fees vary depending on the program. Let's schedule a quick call to discuss the best option for your budget."
            },
            "timing": {
                "keywords": [r"\btiming\b", r"\btimings\b", r"\bwhen\b", r"\bstart\b", r"\bduration\b", r"\bmonths\b", r"\bschedule\b", r"\btime\b"],
                "intent": "timing",
                "stage": "Contacted",
                "reply": "We have new batches starting every month. The standard duration is 12 weeks. Would you prefer a morning or evening batch?"
            },
            "eligibility": {
                "keywords": [r"\beligibility\b", r"\bqualify\b", r"\bdegree\b", r"\bbackground\b", r"\bexperience\b", r"\brequirement\b"],
                "intent": "eligibility",
                "stage": "Qualified",
                "reply": "Most of our programs require a basic understanding of computers, but no prior coding experience is needed. Can you share your educational background?"
            },
            "not_interested": {
                "keywords": [r"\bstop\b", r"\bunsubscribe\b", r"\bnot interested\b", r"\bno thanks\b", r"\bcancel\b"],
                "intent": "not_interested",
                "stage": "Lost",
                "reply": "Thank you for letting us know. We have removed you from our active list. Have a great day!"
            }
        }

    def classify(self, message: str) -> dict:
        msg_lower = message.lower()
        
        # Check rules in order
        for key, rule in self.rules.items():
            for pattern in rule["keywords"]:
                if re.search(pattern, msg_lower):
                    return {
                        "intent": rule["intent"],
                        "suggested_stage": rule["stage"],
                        "reply": rule["reply"]
                    }
        
        # Fallback to 'other'
        return {
            "intent": "other",
            "suggested_stage": "Contacted",
            "reply": "Thank you for reaching out! A counselor will be in touch with you shortly to answer your questions."
        }
