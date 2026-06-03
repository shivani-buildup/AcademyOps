import json
import os
from pathlib import Path
from src.classifier import RuleBasedClassifier

def evaluate():
    base_dir = Path(__file__).parent.parent
    test_file = base_dir / "data" / "intent_test_set.json"
    
    with open(test_file, 'r') as f:
        data = json.load(f)
        
    classifier = RuleBasedClassifier()
    
    correct = 0
    total = len(data)
    
    print("--- Classifier Evaluation Report ---")
    
    for item in data:
        message = item["message"]
        true_intent = item["true_intent"]
        result = classifier.classify(message)
        predicted_intent = result["intent"]
        
        if true_intent == predicted_intent:
            correct += 1
        else:
            print(f"[FAIL] Msg: '{message}'")
            print(f"       Expected: {true_intent} | Got: {predicted_intent}")
            
    accuracy = (correct / total) * 100
    
    print("\n--- Summary ---")
    print(f"Total Messages: {total}")
    print(f"Correctly Classified: {correct}")
    print(f"Accuracy: {accuracy:.2f}%")
    
if __name__ == "__main__":
    evaluate()
