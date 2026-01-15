import os
import requests
import time  # Added for optional retry delays

CHARACTER_FOLDER = "characters"
WORLD_FOLDER = "world"
STORY_FILE = "data/story_recent.txt"

API_URL = "http://127.0.0.1:5000/v1/chat/completions"
API_PARAMS = {
    "mode": "instruct",
    "temperature": 0.8,
    "top_p": 0.9,
    "max_tokens": 800,
}

def load_file(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as file:
            return file.read()
    return ""

def get_ai_response(context, retries=3):
    retry_count = 0
    while retry_count < retries:
        try:
            print(f"Attempting API Call (Try {retry_count + 1}/{retries})...")
            response = requests.post(API_URL, json={"messages": [{"role": "system", "content": context}]})
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()
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
            print("Maximum retries reached. Moving on.")
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

    context = f"""
[Style Guide]
{style_guide}

[World State]
{world_state}

[World Encyclopedia]
{world_encyclopedic}

[Story So Far]
{story_recent}

[Protagonist's Passage]
{protagonist_passage}

[NPCs' Memories]
{'\n'.join(npc_memories)}
"""

    ai_response = get_ai_response(context)
    if ai_response:
        print("\nAI Response:")
        print(ai_response)

        approve = input("\nDo you approve this response? (yes/no): ").strip().lower()
        if approve == "yes":
            with open(STORY_FILE, "a") as story:
                story.write(f"\nProtagonist:\n{protagonist_passage}\n\nNPCs:\n{ai_response}\n")
            print("\nResponse added to story.")
        else:
            print("Response rejected.")

if __name__ == "__main__":
    generate_scene()