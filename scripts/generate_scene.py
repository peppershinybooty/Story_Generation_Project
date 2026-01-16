import os
import requests
from backup_utils import backup_file

CHARACTER_FOLDER = "characters"
WORLD_FOLDER = "world"
STORY_FILE = "data/story_recent.txt"

API_URL = "http://127.0.0.1:5000/v1/chat/completions"

def load_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as file:
            return file.read()
    return ""

def get_ai_response(context, retries=3):
    retry_count = 0
    while retry_count < retries:
        try:
            print(f"Attempting API Call (Try {retry_count + 1}/{retries})...")
            
            payload = {
                "mode": "instruct",
                "messages": [{"role": "user", "content": context}],
                "max_tokens": 800,
                "temperature": 0.8,
                "top_p": 0.9
            }
            
            response = requests.post(API_URL, json=payload, timeout=120)
            
            if response.status_code == 200:
                return response.json()['choices'][0]['message']['content'].strip()
            else:
                print(f"API Error: Status Code {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        retry_count += 1
        if retry_count < retries:
            retry = input("Retry failed API call? (yes/no): ").strip().lower()
            if retry != "yes":
                return None
        else:
            print("Maximum retries reached.")
            return None

def generate_scene():
    npcs = input("Enter characters (NPCs) for this scene, separated by commas: ").split(",")

    print("\nWrite the protagonist's (Liara's) passage. Press Enter twice to finish.")
    protagonist_passage = []
    while True:
        line = input()
        if line == "":
            break
        protagonist_passage.append(line)
    protagonist_passage = "\n".join(protagonist_passage)

    style_guide = load_file(f"{WORLD_FOLDER}/style_guide.txt")
    world_state = load_file(f"{WORLD_FOLDER}/world_state.txt")
    world_encyclopedic = load_file(f"{WORLD_FOLDER}/world_encyclopedic.txt")
    story_recent = load_file(STORY_FILE)

    npc_memories = []
    for npc in npcs:
        npc = npc.strip().lower().replace(" ", "_")
        background = load_file(f"{CHARACTER_FOLDER}/character_{npc}_background.txt")
        shortterm = load_file(f"{CHARACTER_FOLDER}/character_{npc}_shortterm.txt")
        longterm = load_file(f"{CHARACTER_FOLDER}/character_{npc}_longterm.txt")
        if background or shortterm or longterm:
            npc_memories.append(f"NPC [{npc}]:\n{background}\n{shortterm}\n{longterm}")
        else:
            print(f"Warning: No memory files found for NPC '{npc}'. Skipping...")

    context = f"""{style_guide}

WORLD ENCYCLOPEDIA:
{world_encyclopedic}

CURRENT WORLD STATE:
{world_state}

ACTIVE CHARACTERS IN THIS SCENE:
{chr(10).join(npc_memories)}

RECENT STORY:
{story_recent}

CURRENT SCENE:
{protagonist_passage}

Continue the scene. How do the other characters react?"""

    ai_response = get_ai_response(context)
    if ai_response:
        print("\n=== AI RESPONSE ===")
        print(ai_response)
        print("===================\n")

        approve = input("Add to story? (y/n): ").strip().lower()
        if approve == "y":
            # Backup before saving
            backup_file(STORY_FILE)
            
            with open(STORY_FILE, "a", encoding='utf-8') as story:
                story.write(f"\n\n{protagonist_passage}\n\n{ai_response}")
            print("\nSaved to story.")
        else:
            print("Response rejected.")

if __name__ == "__main__":
    generate_scene()