import re
from typing import List, Optional

class HinglishNormalizer:
    """Normalizer for Hinglish text (Hindi+English mix)"""
    
    # Core normalization map for Roman Hindi variations[citation:10]
    HINGLISH_MAP = {
        # Common Roman Hindi variations
        "nhi": "nahi",
        "nai": "nahi", 
        "rha": "raha",
        "rhi": "rahi",
        "rhe": "rahe",
        "aa rha": "aa raha",
        "ho rha": "ho raha",
        "kyu": "kyon",
        "kya": "kya",
        "thik": "theek",
        "sb": "sab",
        "tum": "tum",
        "me": "main",
        
        # Common misspellings
        "complaint": "complaint",
        "hostel": "hostel",
        "water": "water",
        "electricity": "electricity",
    }
    
    # Additional context-aware replacements
    CONTEXT_PATTERNS = [
        (r'\bpaani\b', 'pani'),  # Common spelling variation
        (r'\bbathroom\b', 'bathroom'),
        (r'\btoilet\b', 'toilet'),
        (r'\bmess\b', 'mess'),
        (r'\bwarden\b', 'warden'),
    ]
    
    @staticmethod
    def normalize_hinglish(text: str) -> str:
        """Apply Hinglish normalization rules[citation:10]"""
        if not text:
            return ""
            
        text = text.lower()
        
        # Apply direct replacements
        for pattern, replacement in HinglishNormalizer.CONTEXT_PATTERNS:
            text = re.sub(pattern, replacement, text)
        
        # Apply dictionary replacements (in order)
        for k, v in HinglishNormalizer.HINGLISH_MAP.items():
            text = text.replace(k, v)
        
        return text
    
    @staticmethod
    def clean_whitespace(text: str) -> str:
        """Normalize whitespace and remove extra characters"""
        # Replace multiple spaces, tabs, newlines with single space
        text = re.sub(r'\s+', ' ', text)
        # Remove leading/trailing whitespace
        text = text.strip()
        return text

def preprocess_text(text: str, normalize_hinglish: bool = True) -> str:
    """
    Main preprocessing function for complaint text.
    
    Rules followed[citation:10]:
    1. Lowercasing
    2. Whitespace normalization  
    3. Controlled Hinglish normalization
    4. NO stemming/lemmatization
    5. NO stopword removal
    6. NO translation
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Step 1: Clean whitespace
    cleaned_text = HinglishNormalizer.clean_whitespace(text)
    
    # Step 2: Apply Hinglish normalization if enabled
    if normalize_hinglish:
        cleaned_text = HinglishNormalizer.normalize_hinglish(cleaned_text)
    
    return cleaned_text

def batch_preprocess(texts: List[str], normalize_hinglish: bool = True) -> List[str]:
    """Preprocess multiple texts efficiently"""
    return [preprocess_text(text, normalize_hinglish) for text in texts]

# Example usage
if __name__ == "__main__":
    test_cases = [
        "paani nhi aa rha hostel me",
        "Electricity cut ho gya hai",
        "  Mess   food is not good  ",
        "Warden se complaint karni hai",
    ]
    
    for test in test_cases:
        result = preprocess_text(test)
        print(f"Input: {test}")
        print(f"Output: {result}\n")