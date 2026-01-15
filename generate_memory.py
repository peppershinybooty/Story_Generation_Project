import requests
import os
from datetime import datetime
from backup_utils import backup_file

# Configuration
API_URL = "http://127.0.0.1:5000/v1/completions"
STORY_FOLDER = "."  # Current folder

def get_character_name():
    """Prompt for character name"""
    return input("Character name (e.g., Marcus, Sera): ").strip()

def load_file(filepath):
    """Load text file, return content or None"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def count_shortterm_entries(filepath):
    """Count memory entries in shortterm file"""
    content = load_file(filepath)
    if not content:
        return 0
    # Count entries separated by "---"
    entries = [e.strip() for e in content.split("---") if e.strip()]
    return len(entries)

def call_oobabooga(prompt, max_tokens=400):
    """Send prompt to Oobabooga API"""
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop": ["---END---"]
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['text'].strip()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

def generate_memory(character_name):
    """Generate memory summary for character from latest scene"""
    
    # File paths
    story_file = os.path.join(STORY_FOLDER, "story_recent.txt")
    background_file = os.path.join(STORY_FOLDER, f"character_{character_name}_background.txt")
    shortterm_file = os.path.join(STORY_FOLDER, f"character_{character_name}_shortterm.txt")
    
    # Load files
    story = load_file(story_file)
    background = load_file(background_file)
    
    if not story:
        print(f"Error: {story_file} not found")
        return
    
    if not background:
        print(f"Error: {background_file} not found")
        return
    
    # Build prompt
    prompt = f"""You are summarizing a scene from {character_name}'s perspective.

CHARACTER BACKGROUND:
{background}

RECENT SCENE:
{story}

Task: Write a brief memory summary (2-4 sentences) from {character_name}'s first-person perspective about what they observed, experienced, or learned in this scene. Focus on:
- What they saw others do or say
- Their own actions
- Important information they learned
- Emotions they felt (without announcing internal thoughts to others)

Do NOT include what others were thinking. Only what {character_name} could observe.

Memory summary:"""

    print(f"\nGenerating memory for {character_name}...")
    memory = call_oobabooga(prompt, max_tokens=200)
    
    if not memory:
        print("Failed to generate memory")
        return
    
    print("\n--- GENERATED MEMORY ---")
    print(memory)
    print("------------------------\n")
    
    save = input("Save this memory? (y/n): ").strip().lower()
    
    if save == 'y':
        # Backup shortterm file before modifying
        backup_file(shortterm_file)
        
        # Add timestamp and separator
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n---\n[{timestamp}]\n{memory}\n"
        
        # Append to shortterm file
        with open(shortterm_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        print(f"Memory saved to {shortterm_file}")
        
        # Check entry count
        count = count_shortterm_entries(shortterm_file)
        print(f"\nShortterm memory entries: {count}/10")
        
        if count >= 10:
            print(f"⚠️  WARNING: {character_name} has 10+ shortterm memories!")
            print(f"Run: python consolidate_memories.py")
    else:
        print("Memory discarded")

def main():
    print("=== GENERATE CHARACTER MEMORY ===\n")
    character_name = get_character_name()
    
    if not character_name:
        print("No character name provided")
        return
    
    generate_memory(character_name)

if __name__ == "__main__":
    main()