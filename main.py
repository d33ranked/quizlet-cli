import sys
from config import setup_game_data
from game import play_game

def main():
    # Destructure all 3 configuration states
    words, reverse, max_rounds = setup_game_data()

    if words is None:
        print("Usage: python main.py game [--reverse] [--profile name] [--total count]")
        sys.exit(0)

    # Pass max_rounds configuration into our tracking game loop
    play_game(words, reverse=reverse, max_rounds=max_rounds)

if __name__ == "__main__":
    main()