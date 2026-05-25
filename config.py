import argparse
import json
import os
import sys

import word_filter_rules

WORDS_FILE = "german.json"
class WordFilter:
    def __init__(self, word_obj):
        self.word_obj = word_obj
        self.accepted = True
        self._rules = []

    def add_rule(self, rule_func, *args, **kwargs):
        """Appends a rule function and its contextual arguments to the pipeline."""
        self._rules.append((rule_func, args, kwargs))
        return self  # Enables chaining if desired

    def execute(self):
        """
        Executes each appended rule sequentially. 
        If accepted becomes False, it skips the remaining rules entirely.
        """
        for rule_func, args, kwargs in self._rules:
            if not self.accepted:
                break
            # Execute the rule, passing the current word and any stored filter arguments
            self.accepted = rule_func(self.word_obj, *args, **kwargs)
            
        return self

def load_json_file(json_path, error_msg):
    """Safely loads a JSON file or exits on error."""
    if not os.path.exists(json_path):
        print(f"Error: File not found at {json_path}")
        sys.exit(1)
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON from {json_path}")
        sys.exit(1)

def parse_cefr_range(level_str):
    """
    Converts a range string like 'A1:B1' into a list of inclusive levels.
    If it's a single level like 'A2', it returns ['A2'].
    """
    all_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    if ":" in level_str:
        try:
            start, end = level_str.split(":")
            start_idx = all_levels.index(start.strip().upper())
            end_idx = all_levels.index(end.strip().upper())
            # Return the slice inclusively
            return all_levels[start_idx : end_idx + 1]
        except (ValueError, IndexError):
            print(f"Warning: Invalid CEFR range '{level_str}'. Disabling level filter.")
            return all_levels
    else:
        return [level_str.strip().upper()]

def filter_words(words, filters):
    """Filters words in-memory using the WordFilter pipeline pattern."""
    filtered_list = []
    
    # Pre-parse the CEFR levels range if present
    allowed_levels = None
    if "cefr_level" in filters:
        allowed_levels = parse_cefr_range(filters["cefr_level"])

    for word_obj in words:
        # Initialize the pipeline for this specific word
        pipeline = WordFilter(word_obj)
        
        # Build the pipeline steps
        pipeline.add_rule(word_filter_rules.cefr_level_rule, allowed_levels=allowed_levels)
        pipeline.add_rule(word_filter_rules.dynamic_boolean_rule, profile_filters=filters)
        
        # Execute processing steps
        result = pipeline.execute()
        
        # Gather results
        if result.accepted:
            filtered_list.append(word_obj)

    return filtered_list

def parse_cli_arguments():
    """Defines and parses CLI arguments including target round limit."""
    parser = argparse.ArgumentParser(description="German CLI Learning Game")
    subparsers = parser.add_subparsers(dest="command")
    game_parser = subparsers.add_parser("game", help="Start the game")

    game_parser.add_argument("--data", type=str, default=WORDS_FILE, help="Path to words JSON")
    game_parser.add_argument("--reverse", action="store_true", help="Play English to German")
    game_parser.add_argument("--profile", type=str, help="Name of the saved profile to load")
    # Added --total flag for limited-round game sessions
    game_parser.add_argument("--total", type=int, default=None, help="Number of words to test before auto-exiting")

    args, unknown_args = parser.parse_known_args()
    return args

def setup_game_data():
    """Orchestrates parsing profiles and filtering the word list."""
    args = parse_cli_arguments()

    if args.command != "game":
        return None, False, None

    words = load_json_file(args.data, "words database")
    filters = {}

    if args.profile:
        profiles_db = load_json_file("profiles.json", "profiles registry")
        if args.profile in profiles_db:
            print(f"Loaded profile config: '{args.profile}'")
            filters = profiles_db[args.profile]
        else:
            print(f"Error: Profile '{args.profile}' not found in profiles.json")
            sys.exit(1)

    if filters:
        print(f"Applying profile rules: {filters}")
        words = filter_words(words, filters)
        print(f"Pool size: {len(words)} words.")

    # Return total rounds parameter alongside word pool and mode
    return words, args.reverse, args.total