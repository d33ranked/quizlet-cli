import random

def play_game(words, reverse=False, max_rounds=None):
    """Runs the core CLI game loop, automatically stopping if max_rounds is met."""
    if not words:
        print("No words matched your profile criteria! Game over before it started.")
        return

    print("\n--- Willkommen zum Deutschlernen! ---")
    if max_rounds:
        print(f"Game Mode: Quick session of {max_rounds} words.")
    print("Type 'exit' or 'quit' at any time to stop playing and view results.\n")

    score = 0
    total_rounds = 0
    incorrect_words_pool = {}

    while True:
        word_obj = random.choice(words)

        if reverse:
            translations = [t.strip() for t in word_obj["english_translation"].split(";")]
            prompt = random.choice(translations)
            correct_answers = [word_obj["word"]]
            display_prompt = f"Translate to German: '{prompt}'"
        else:
            prompt = word_obj["word"]
            correct_answers = [t.strip().lower() for t in word_obj["english_translation"].split(";")]
            display_prompt = f"Translate to English: '{prompt}'"

        if word_obj.get("pos"):
            display_prompt += f" ({word_obj['pos']})"

        # Show progress if max_rounds is active (e.g., "[1/5] Translate...")
        prefix = f"[{total_rounds + 1}/{max_rounds}] " if max_rounds else ""
        print(f"{prefix}{display_prompt}")
        user_input = input("> ").strip()

        if user_input.lower() in ["exit", "quit"]:
            break

        total_rounds += 1

        # Check answers
        if reverse:
            if word_obj.get("capitalization_sensitive", False):
                is_correct = user_input == correct_answers[0]
            else:
                is_correct = user_input.lower() == correct_answers[0].lower()
        else:
            is_correct = user_input.lower() in correct_answers

        if is_correct:
            print("✅ Correct!\n")
            score += 1
        else:
            actual_answers = ", ".join(correct_answers)
            print(f"❌ Wrong. The correct answer was: {actual_answers}")
            if word_obj.get("example_sentence_native"):
                print(f"Hint: {word_obj['example_sentence_native']}")
            print()
            incorrect_words_pool[word_obj["word"]] = word_obj

        # AUTO-EXIT CONDITION: Stop when limit is met
        if max_rounds and total_rounds >= max_rounds:
            print("🎉 Session complete! Calculating your performance summary...")
            break

    # --- GAME RESULTS SUMMARY ---
    print("\n========================================")
    print("             GAME RESULTS               ")
    print("========================================")
    print(f"Score: {score} / {total_rounds}")
    
    if total_rounds > 0:
        percentage = (score / total_rounds) * 100
        print(f"Accuracy: {percentage:.1f}%")
    
    if incorrect_words_pool:
        print("\n📚 Words to Review:")
        print("----------------------------------------")
        for word, obj in incorrect_words_pool.items():
            print(f"• German: {obj['word']} ({obj.get('pos', 'N/A')})")
            print(f"  English: {obj['english_translation']}")
            if obj.get("example_sentence_native"):
                print(f"  Example: {obj['example_sentence_native']}")
                print(f"  Translation: {obj.get('example_sentence_english', 'N/A')}")
            print("-" * 40)
    else:
        if total_rounds > 0:
            print("\n🎉 Perfect round! No incorrect words to display.")
            
    print("\nDanke fürs Spielen! Tschüss!")