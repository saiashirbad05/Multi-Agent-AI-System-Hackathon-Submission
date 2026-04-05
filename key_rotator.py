"""Auto-rotating API key manager — cycles through keys on 429 errors."""
import os
import time
from dotenv import load_dotenv
load_dotenv()

KEYS = [v for k, v in sorted(os.environ.items()) 
        if k.startswith("GOOGLE_API_KEY") and v.startswith("AIza")]

current_index = 0

def get_current_key():
    return KEYS[current_index] if KEYS else None

def rotate_key():
    global current_index
    current_index = (current_index + 1) % len(KEYS)
    new_key = KEYS[current_index]
    os.environ["GOOGLE_API_KEY"] = new_key
    print(f"Rotated to key {current_index + 1}/{len(KEYS)}")
    return new_key

print(f"Loaded {len(KEYS)} API keys")
print(f"Active key: key 1 ending in ...{KEYS[0][-6:] if KEYS else 'NONE'}")
