#!/usr/bin/env python3
"""
Urgency anchor definitions for similarity-based urgency detection.
Each urgency level has multilingual anchors that represent severity signals.
"""

URGENCY_ANCHORS = {
    "Low": [
        "Tap is leaking slightly in washroom",
        "Room light is dim",
        "WiFi speed is a bit slow sometimes",
        "Fan makes small noise but works",
        "Water pressure is slightly low",
        "Door handle is loose"
    ],

    "Medium": [
        "WiFi not working properly since yesterday",
        "Bathroom is dirty and needs cleaning",
        "Paani ka pressure kaafi kam hai",
        "Fan not working properly",
        "Mess food quality is bad today",
        "No hot water in the morning"
    ],

    "High": [
        "No water supply since morning",
        "Power cut for many hours",
        "Toilet is blocked and unusable",
        "Room fan completely not working",
        "Internet down during exams",
        "Washroom overflowing with water"
    ],

    "Critical": [
        "Electric spark coming from switch",
        "Water leakage near electric board",
        "Unknown person roaming inside hostel",
        "Hostel gate open at night",
        "Fight happened near hostel",
        "Street lights not working near hostel gate"
    ]
}

URGENCY_DESCRIPTIONS = {
    "Low": "Minor inconvenience, no immediate action required",
    "Medium": "Affects daily routine, should be addressed soon",
    "High": "Serious disruption, needs quick action",
    "Critical": "Safety or security risk — immediate action required"
}

URGENCY_LEVELS = ["Low", "Medium", "High", "Critical"]

# Response time guidelines (in hours)
URGENCY_RESPONSE_TIMES = {
    "Low": 72,      # Within 3 days
    "Medium": 24,   # Within 1 day
    "High": 6,      # Within 6 hours
    "Critical": 1   # Within 1 hour
}

# Priority weights (for sorting)
URGENCY_WEIGHTS = {
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}

def get_all_urgency_levels() -> list:
    """Get list of all urgency levels"""
    return URGENCY_LEVELS.copy()

def get_urgency_anchors(level: str) -> list:
    """Get anchor sentences for a specific urgency level"""
    return URGENCY_ANCHORS.get(level, [])

def get_urgency_description(level: str) -> str:
    """Get description for an urgency level"""
    return URGENCY_DESCRIPTIONS.get(level, "No description available")

def get_response_time_hours(level: str) -> int:
    """Get recommended response time in hours"""
    return URGENCY_RESPONSE_TIMES.get(level, 24)

def get_urgency_weight(level: str) -> int:
    """Get priority weight for sorting"""
    return URGENCY_WEIGHTS.get(level, 1)

def validate_urgency_level(level: str) -> bool:
    """Check if an urgency level is valid"""
    return level in URGENCY_LEVELS

def get_anchor_count() -> int:
    """Get total number of urgency anchor sentences"""
    return sum(len(anchors) for anchors in URGENCY_ANCHORS.values())

if __name__ == "__main__":
    # Print summary
    print("Urgency Anchor System Summary")
    print("=" * 60)
    
    for level in URGENCY_LEVELS:
        anchors = URGENCY_ANCHORS[level]
        description = URGENCY_DESCRIPTIONS[level]
        response_time = URGENCY_RESPONSE_TIMES[level]
        
        print(f"\n{level}:")
        print(f"  Description: {description}")
        print(f"  Response Time: {response_time} hours")
        print(f"  Anchors: {len(anchors)}")
        print(f"  Sample: '{anchors[0]}'")
    
    print(f"\nTotal anchors: {get_anchor_count()}")
    print(f"Total urgency levels: {len(URGENCY_LEVELS)}")