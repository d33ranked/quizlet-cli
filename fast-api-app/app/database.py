import os
import json
import redis

# 1. Define the exact variables main.py is looking for at the top level
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
WORD_POOL_KEY = "all_words"

def init_db():
    """
    Checks if the Redis word pool is empty. If it is, reads the local
    words.json file and populates the database before the app loads.
    """
    print("Checking database status...")
    
    try:
        r.ping()
    except redis.ConnectionError as e:
        print(f"CRITICAL: Could not connect to Redis: {e}")
        return

    if r.scard(WORD_POOL_KEY) == 0:
        print("Redis is empty! Starting data population script...")
        
        # Safely locate words.json in the same folder as this file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, "words.json")
        
        if not os.path.exists(json_path):
            print(f"CRITICAL: Could not find data file at {json_path}")
            return
            
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                word_list = json.load(file)
            
            pipe = r.pipeline()
            for entry in word_list:
                word = entry.get("word")
                if not word:
                    continue
                
                redis_hash_data = {
                    "useful_for_flashcard": str(entry.get("useful_for_flashcard", False)),
                    "cefr_level": entry.get("cefr_level", ""),
                    "english_translation": entry.get("english_translation", ""),
                    "romanization": entry.get("romanization", ""),
                    "example_sentence_native": entry.get("example_sentence_native", ""),
                    "example_sentence_english": entry.get("example_sentence_english", ""),
                    "gender": entry.get("gender", ""),
                    "is_separable_verb": str(entry.get("is_separable_verb", False)),
                    "separable_prefix": entry.get("separable_prefix", ""),
                    "base_verb": entry.get("base_verb", ""),
                    "capitalization_sensitive": str(entry.get("capitalization_sensitive", False)),
                    "pos": entry.get("pos", ""),
                    "word_frequency": str(entry.get("word_frequency", 0))
                }
                
                redis_key = f"word:{word.lower()}"
                pipe.hset(redis_key, mapping=redis_hash_data)
                pipe.sadd(WORD_POOL_KEY, word.lower())
            
            pipe.execute()
            print(f"Successfully populated Redis with {len(word_list)} words.")
            
        except Exception as e:
            print(f"CRITICAL: Failed to seed data from JSON: {e}")
    else:
        print("Database already contains data. Skipping population.")