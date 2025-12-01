# The starting state for the Context Agent.
# This ensures that even if the agent detects nothing, we have valid values.

DEFAULT_CONTEXT = {
    # TRANSLATION DIRECTION
    "Source_Language": "English",
    "Target_Language": "Vietnamese",

    # SPEAKER PROFILE (User)
    "Speaker_Name": "User",
    "Speaker_Gender": "Neutral",
    "Speaker_Age": "Unknown",
    "Speaker_Regional_Dialect": "General American", 

    # AUDIENCE PROFILE (Them)
    "Audience_Name": "Unknown",
    "Audience_Gender": "Neutral", 
    "Audience_Age": "Unknown",
    "Audience_Regional_Dialect": "Northern", # Default to Hanoi dialect for output

    # SETTING & TONE
    "Relationship": "Strangers",
    "Setting_Location": "General",
    "Setting_Time": "Daytime",
    "Tone": "Polite / Neutral",

    # CRITICAL CONSTRAINTS
    "Taboo_Behavior": "None",       # e.g., "Pointing fingers", "Talking loudly"
    "Taboo_Phrases": "None"         # e.g., "Profanity", "Mentioning politics"
}
