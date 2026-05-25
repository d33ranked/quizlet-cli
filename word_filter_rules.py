def cefr_level_rule(word_obj, allowed_levels):
    """Returns True if the word's level is within allowed levels, False otherwise."""
    if not allowed_levels:
        return True
    return word_obj.get("cefr_level") in allowed_levels


def dynamic_boolean_rule(word_obj, profile_filters):
    """
    Iterates over profile keys. If a key maps to a boolean profile value, 
    verifies it matches the word object. Non-boolean keys are safely ignored.
    """
    for key, val in profile_filters.items():
        # Skip the CEFR level key since it has its own dedicated rule
        if key == "cefr_level":
            continue

        # CRITICAL FIX: Only evaluate if the profile config value is explicitly a boolean
        if isinstance(val, bool):
            if key in word_obj:
                if word_obj.get(key) != val:
                    return False  # Failed match
            else:
                return False  # Key missing entirely from word dictionary
                
        # If it's not a boolean value in profiles.json, we safely ignore it and continue
    return True