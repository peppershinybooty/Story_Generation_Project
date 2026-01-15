import os
import glob
import requests
from datetime import datetime
from backup_utils import backup_file

# Config - change API_URL if your oobabooga uses a different port/path
API_URL = "http://127.0.0.1:5000/v1/completions"
STORY_FILE = "story_recent.txt"
SHORTTERM_TEMPLATE = "character_{}_shortterm.txt"
BACKGROUND_TEMPLATE = "character_{}_background.txt"

# Prompt template (keeps same rules as generate_memory.py)
PROMPT_TEMPLATE = """You are summarizing a scene from {character}'s perspective.

CHARACTER BACKGROUND:
{background}

RECENT SCENE:
{story}

Task: Write a brief memory summary (2-4 sentences) from {character}'s first-person perspective about what they observed, experienced, or learned in this scene. Focus on:
- What they saw others do or say
- Their own actions
- Important information they learned
- Emotions they felt (without announcing internal thoughts to others)

Do NOT include what others were thinking. Only what {character} could observe.

Memory summary:"""

def load_file(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def call_oobabooga(prompt, max_tokens=200):
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop": ["---END---"]
    }
    try:
        r = requests.post(API_URL, json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        # match generate_memory.py behavior: choices[0]['text']
        return data['choices'][0].get('text', '').strip()
    except Exception as e:
        print(f"API error: {e}")
        return None

def count_entries(shortterm_path):
    content = load_file(shortterm_path)
    if not content:
        return 0
    entries = [e.strip() for e in content.split("---") if e.strip()]
    return len(entries)

def append_memory(shortterm_path, memory):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    backup_file(shortterm_path)
    with open(shortterm_path, "a", encoding="utf-8") as f:
        f.write(f"\n[{timestamp}]\n{memory}\n---\n")
    print(f"Saved memory to {shortterm_path}")

def main():
    print("BATCH MEMORY GENERATOR\n")
    story = load_file(STORY_FILE)
    if not story:
        print(f"Error: {STORY_FILE} not found or empty. Run a scene first.")
        return

    # Find all background files: character_*_background.txt
    bg_files = glob.glob("character_*_background.txt")
    if not bg_files:
        print("No characters found (no character_*_background.txt files).")
        return

    # Ask whether to auto-save all (y) or prompt per character (n)
    auto = input("Auto-save all generated memories? (y/N): ").strip().lower() == "y"

    for bg_path in bg_files:
        # Extract name, e.g., character_marcus_background.txt -> marcus
        basename = os.path.basename(bg_path)
        parts = basename.split("_")
        if len(parts) < 3:
            continue
        char_name = "_".join(parts[1:-1])  # supports multi-word names like 'van_der'
        display_name = char_name.replace("_", " ").title()

        background = load_file(bg_path)
        shortterm_path = SHORTTERM_TEMPLATE.format(char_name)
        if not background:
            print(f"Skipping {display_name}: background file empty.")
            continue
        if not os.path.exists(shortterm_path):
            # create an initial shortterm file if missing
            with open(shortterm_path, "w", encoding="utf-8") as f:
                f.write(f"CHARACTER: {display_name}\nSHORT-TERM MEMORY (Recent detailed memories - last 10 scenes):\n\n")
            print(f"Created missing shortterm file: {shortterm_path}")

        prompt = PROMPT_TEMPLATE.format(character=display_name, background=background, story=story)
        print(f"\nGenerating memory for {display_name}...")
        memory = call_oobabooga(prompt, max_tokens=200)
        if not memory:
            print(f"Failed to generate memory for {display_name}.")
            continue

        print("\n--- GENERATED MEMORY ---")
        print(memory)
        print("------------------------")

        save = auto
        if not auto:
            answer = input(f"Save memory for {display_name}? (y/N): ").strip().lower()
            save = answer == "y"

        if save:
            append_memory(shortterm_path, memory)
            entries = count_entries(shortterm_path)
            if entries >= 10:
                print(f"⚠️  {display_name} has {entries} short-term memories. Consider running consolidate_memories.py.")
        else:
            print(f"Skipped saving memory for {display_name}.")

    print("\nBatch run complete.")

if __name__ == "__main__":
    main()