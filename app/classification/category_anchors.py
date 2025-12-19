#!/usr/bin/env python3
"""
Category anchor definitions for similarity-based classification.
Each category has multilingual anchors that represent its semantic space.
"""

CATEGORY_ANCHORS = {
    "Water": [
        "No water supply in hostel",
        "Paani nahi aa raha hostel me",
        "Water pressure bahut low hai",
        "Bathroom me paani nahi aa raha",
        "Since morning water problem in hostel",
        "Tap se pani bohot kam aa raha"
    ],

    "Electricity": [
        "Frequent power cuts at night",
        "Bijli baar baar ja rahi hai",
        "Light nahi hai room me",
        "Switch se spark aa raha hai",
        "Power cut since last night",
        "Fan aur light dono nahi chal rahe"
    ],

    "Internet": [
        "WiFi is very slow",
        "Wifi ka issue hai hostel me",
        "Internet disconnect ho raha hai",
        "No internet in my room",
        "Wifi not working on this floor",
        "Speed bohot slow ho gayi hai"
    ],

    "Hygiene": [
        "Washrooms are not cleaned properly",
        "Washroom saaf nahi ho raha",
        "Bad smell near hostel area",
        "Dustbin bhara hua hai",
        "Bathroom me gandagi hai",
        "Cleaning staff properly kaam nahi kar raha"
    ],

    "Mess": [
        "Food quality is very bad",
        "Mess ka khana kharab hai",
        "Found insects in food",
        "Khana theek se paka nahi hai",
        "Mess food is unhygienic",
        "Breakfast quality is very poor"
    ],

    "Infrastructure": [
        "Fan not working in my room",
        "Room ka fan kharab hai",
        "Water leakage from ceiling",
        "Window glass is broken",
        "Door lock is not working",
        "Ceiling fan making noise"
    ],

    "Noise": [
        "Too much noise at night",
        "Raat ko bahut shor hota hai",
        "Loud music in hostel",
        "Exam time me disturbance ho raha",
        "Nearby room me bohot awaaz hai",
        "Late night noise issue"
    ],

    "Safety": [
        "Unknown person seen near hostel gate",
        "Raat ko gate ke paas ajeeb log the",
        "Street lights not working near hostel",
        "Fight broke out near mess",
        "Security guard not present at gate",
        "Hostel gate open at night"
    ],

    "Administration": [
        "Warden is not responding",
        "Warden sunta hi nahi hai",
        "Caretaker not taking action",
        "Complaint ka koi response nahi mila",
        "Staff delays action on complaints",
        "Office se koi reply nahi aa raha"
    ],

    "Others": [
        "General inconvenience faced by students",
        "Hostel facilities improve karni chahiye",
        "Overall hostel experience is bad",
        "Students are facing many problems",
        "Management should look into issues"
    ]
}

# Category descriptions for documentation
CATEGORY_DESCRIPTIONS = {
    "Water": "Issues related to water supply, pressure, or quality",
    "Electricity": "Power outages, electrical faults, or appliance issues",
    "Internet": "WiFi connectivity, speed, or network problems",
    "Hygiene": "Cleanliness, sanitation, or hygiene concerns",
    "Mess": "Food quality, hygiene, or mess-related issues",
    "Infrastructure": "Room facilities, furniture, or building maintenance",
    "Noise": "Disturbances, loud noise, or peace violations",
    "Safety": "Security concerns, unauthorized persons, or safety hazards",
    "Administration": "Staff responsiveness, warden issues, or administrative delays",
    "Others": "General complaints not fitting other categories"
}

def get_all_categories() -> list:
    """Get list of all category names"""
    return list(CATEGORY_ANCHORS.keys())

def get_category_anchors(category: str) -> list:
    """Get anchor sentences for a specific category"""
    return CATEGORY_ANCHORS.get(category, [])

def get_category_description(category: str) -> str:
    """Get description for a category"""
    return CATEGORY_DESCRIPTIONS.get(category, "No description available")

def get_anchor_count() -> int:
    """Get total number of anchor sentences"""
    return sum(len(anchors) for anchors in CATEGORY_ANCHORS.values())

if __name__ == "__main__":
    # Print summary
    print("Category Anchor Summary")
    print("=" * 50)
    for category, anchors in CATEGORY_ANCHORS.items():
        print(f"{category}: {len(anchors)} anchors")
    print(f"\nTotal anchors: {get_anchor_count()}")
    print(f"Total categories: {len(CATEGORY_ANCHORS)}")