import requests
import json
import os
from backup_utils import backup_file

# Configuration
API_URL = "http://127.0.0.1:5000/v1/chat/completions"
STORY_FOLDER = "."  # Current folder

def load_file(filename):
    """Load content from a text file"""
    try:
        with open(os.path.join(STORY_FOLDER, filename), 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Warning: {filename} not found")
        return ""

def save_to_story(content):
    """Append content to story_recent.txt with backup"""
    story_file = os.path.join(STORY_FOLDER, "story_recent.txt")
    
    # Backup before modifying
    backup_file(story_file)
    
    with open(story_file, 'a', encoding='utf-8') as f:
        f.write("\n\n" + content)

def load_character_memory(character_name):
    """Load all 3 memory tiers for a character"""
    char_lower = character_name.lower().strip().replace(" ", "_")
    
    background = load_file(f"character_{char_lower}_background.txt")
    shortterm = load_file(f"character_{char_lower}_shortterm.txt")
    longterm = load_file(f"character_{char_lower}_longterm.txt")
    
    # Combine into one block
    full_memory = f"{background}\n\n{longterm}\n\n{shortterm}"
    return full_memory

def generate_scene(characters_present, liara_passage):
    """Generate the scene with AI"""
    
    # Load world files
    world_state = load_file("world_state.txt")
    world_encyclopedic = load_file("world_encyclopedic.txt")
    style_guide = load_file("style_guide.txt")
    recent_story = load_file("story_recent.txt")
    
    # Load character memories for those present
    character_info = ""
    for char in characters_present:
        char_memory = load_character_memory(char)
        if char_memory:
            character_info += f"\n{'='*50}\n{char_memory}\n"
    
    # Build the full prompt
    prompt = f"""{style_guide}

WORLD ENCYCLOPEDIA:
{world_encyclopedic}

CURRENT WORLD STATE:
{world_state}

ACTIVE CHARACTERS IN THIS SCENE:
{character_info}

RECENT STORY:
{recent_story}

CURRENT SCENE:
{liara_passage}

Continue the scene. How do the other characters react?"""
    
    # Send to Oobabooga API
    payload = {
        "mode": "instruct",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 800,
        "temperature": 0.8,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content']
    except Exception as e:
        return f"Error generating scene: {e}"

def main():
    print("=== COLLABORATIVE STORYTELLING GENERATOR ===\n")
    
    # Get characters present
    chars_input = input("Who is present in this scene? (comma-separated names): ")
    characters = [c.strip() for c in chars_input.split(",")]
    
    print(f"\nCharacters loaded: {', '.join(characters)}")
    print("\nWrite your scene (Liara's passage). Press Enter twice when done:\n")
    
    # Multi-line input
    lines = []
    while True:
        line = input()
        if line == "" and lines and lines[-1] == "":
            break
        lines.append(line)
    
    liara_passage = "\n".join(lines[:-1])
    
    print("\n[Generating...]\n")
    
    # Generate the scene
    ai_response = generate_scene(characters, liara_passage)
    
    print("=== AI RESPONSE ===")
    print(ai_response)
    print("\n==================\n")
    
    # Ask to save
    save = input("Add to story? (y/n): ").lower()
    if save == 'y':
        save_to_story(liara_passage)
        save_to_story(ai_response)
        print("Saved to story_recent.txt")
    
    again = input("\nGenerate another scene? (y/n): ").lower()
    if again == 'y':
        main()
    else:
        print("Done!")

if __name__ == "__main__":
    main()