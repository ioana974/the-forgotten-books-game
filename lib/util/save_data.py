import json
import os

SAVE_PATH = "game_save.json"

wrong_answers_memory = {}

game_data = {
    "narrator_intro_done": False,
    "unlocked_levels": [False, False, False, False, False, False],
    "narrator_read_rules": False,
    "music_on": True,
    "narrator_oh_you_found_this": False, 
    "lvl1_card_shown": False, 
    "lvl1_completed": False, 
    "lv1_best_score": 0,
    "language": "RO",
}

def save_progress():
    with open(SAVE_PATH, "w") as f:
        json.dump(game_data, f)

def load_progress():
    if os.path.exists(SAVE_PATH):
        with open(SAVE_PATH, "r") as f:
            saved = json.load(f)
            game_data.update(saved)
