#!/usr/bin/env python3
"""
Verify preprocessing fixes similarity issues
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.preprocessing.text_cleaner import preprocess_text
from app.services.embedding_service import get_embedding_service
from app.issues.similarity import cosine_similarity

embedding_service = get_embedding_service()

test_cases = [
    # English-Hindi pairs (should be high similarity after preprocessing)
    ("No water supply in BH-3 since morning", "Paani nahi aa raha BH-3 me subah se"),
    ("Electricity cut in hostel", "Bijli chali gayi hostel me"),
    ("WiFi not working", "Wifi kaam nahi kar raha"),
    
    # English-English variations
    ("No water in BH-3", "Water problem BH-3"),
    ("Electricity issue", "Power cut problem"),
    
    # Same text (should be 1.0)
    ("No water supply", "No water supply"),
]

print("🔍 Verifying Preprocessing Fix")
print("=" * 60)
print("\nWithout preprocessing:")
print("-" * 40)

for text1, text2 in test_cases[:3]:  # Just first 3 for comparison
    # Without preprocessing
    emb1_raw = embedding_service.generate_embedding(text1, normalize_hinglish=True)
    emb2_raw = embedding_service.generate_embedding(text2, normalize_hinglish=True)
    sim_raw = cosine_similarity(emb1_raw, emb2_raw)
    
    # With preprocessing
    clean1 = preprocess_text(text1, normalize_hinglish=True)
    clean2 = preprocess_text(text2, normalize_hinglish=True)
    emb1_clean = embedding_service.generate_embedding(clean1, normalize_hinglish=False)
    emb2_clean = embedding_service.generate_embedding(clean2, normalize_hinglish=False)
    sim_clean = cosine_similarity(emb1_clean, emb2_clean)
    
    print(f"\n'{text1[:40]}...'")
    print(f"'{text2[:40]}...'")
    print(f"Raw similarity: {sim_raw:.4f}")
    print(f"Preprocessed: {sim_clean:.4f} (Δ: {sim_clean - sim_raw:+.4f})")
    print(f"Clean texts: '{clean1[:40]}...' | '{clean2[:40]}...'")

print("\n\nWith preprocessing (all tests):")
print("-" * 40)

for text1, text2 in test_cases:
    clean1 = preprocess_text(text1, normalize_hinglish=True)
    clean2 = preprocess_text(text2, normalize_hinglish=True)
    
    emb1 = embedding_service.generate_embedding(clean1, normalize_hinglish=False)
    emb2 = embedding_service.generate_embedding(clean2, normalize_hinglish=False)
    
    similarity = cosine_similarity(emb1, emb2)
    
    print(f"\n'{text1[:30]}...'")
    print(f"'{text2[:30]}...'")
    print(f"→ '{clean1[:30]}...'")
    print(f"→ '{clean2[:30]}...'")
    print(f"Similarity: {similarity:.4f}")
    print(f"Duplicate (0.88): {'✅' if similarity >= 0.88 else '❌'}")
