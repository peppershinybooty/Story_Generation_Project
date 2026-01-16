import requests
import os
from datetime import datetime
from backup_utils import backup_file

# Configuration
API_URL = "http://127.0.0.1:5000/v1/completions"
STORY_FOLDER = "."  # Current folder

def get_character_name():
    """Prompt for character name"""
    return input("Character name to consolidate: ").strip()

def load_file(filepath):
    """Load text file, return content or None"""
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def call_oobabooga(prompt, max_tokens=600):
    """Send prompt to Oobabooga API"""
    payload = {
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
        "stop": ["---END---"]
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=90)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['text'].strip()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

def consolidate_memories(character_name):
    """Consolidate shortterm memories into longterm summary"""
    
    # File paths
    char_lower = character_name.lower().strip().replace(" ", "_")
    background_file = os.path.join(STORY_FOLDER, f"character_{char_lower}_background.txt")
    shortterm_file = os.path.join(STORY_FOLDER, f"character_{char_lower}_shortterm.txt")
    longterm_file = os.path.join(STORY_FOLDER, f"character_{char_lower}_longterm.txt")
    
    # Load files
    background = load_file(background_file)
    shortterm = load_file(shortterm_file)
    
    if not background:
        print(f"Error: {background_file} not found")
        return
    
    if not shortterm or shortterm.strip() == "":
        print(f"Error: No shortterm memories found for {character_name}")
        return
    
    # Count entries
    entries = [e.strip() for e in shortterm.split("---") if e.strip()]
    entry_count = len(entries)
    
    print(f"\nFound {entry_count} shortterm memories for {character_name}")
    
    if entry_count < 5:
        print(f"Warning: Only {entry_count} entries. Consider waiting until 10+ before consolidating.")
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed != 'y':
            print("Consolidation cancelled")
            return
    
    # Build consolidation prompt
    prompt = f"""You are consolidating {character_name}'s recent memories into a summary.

CHARACTER BACKGROUND:
{background}

RECENT SHORTTERM MEMORIES (LAST {entry_count} SCENES):
{shortterm}

Task: Write a consolidated summary (4-8 sentences) in first-person from {character_name}'s perspective that captures:
- Key events they witnessed or participated in
- Important relationships that developed or changed
- Critical information they learned
- Significant emotional moments or realizations
- Any ongoing concerns or goals they developed

Focus on what's important for {character_name} to remember long-term. Compress similar events together. Keep specific details that matter.

Consolidated memory summary:"""

    print(f"\nGenerating consolidated summary...")
    summary = call_oobabooga(prompt, max_tokens=400)
    
    if not summary:
        print("Failed to generate consolidated summary")
        return
    
    print("\n" + "="*60)
    print("CONSOLIDATED SUMMARY:")
    print("="*60)
    print(summary)
    print("="*60 + "\n")
    
    save = input("Save this consolidated summary? (y/n): ").strip().lower()
    
    if save == 'y':
        # Backup files before making changes
        backup_file(shortterm_file)
        if os.path.exists(longterm_file):
            backup_file(longterm_file)
        
        # Now make changes
        # Add to longterm
        consolidation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n---\n[{consolidation_timestamp}] Consolidated from {entry_count} memories:\n{summary}\n"
        
        with open(longterm_file, 'a', encoding='utf-8') as f:
            f.write(entry)
        
        print(f"✓ Added consolidated summary to {longterm_file}")
        
        # Clear shortterm file (keep header)
        header = f"""CHARACTER: {character_name}
SHORT-TERM MEMORY (Recent detailed memories - last 10 scenes):

"""
        with open(shortterm_file, 'w', encoding='utf-8') as f:
            f.write(header)
        
        print(f"✓ Cleared {shortterm_file}")
        print(f"\n✓ Consolidation complete for {character_name}")
    else:
        print("Consolidation cancelled - no changes made")

def main():
    print("=== CONSOLIDATE CHARACTER MEMORIES ===\n")
    character_name = get_character_name()
    
    if not character_name:
        print("No character name provided")
        return
    
    consolidate_memories(character_name)

if __name__ == "__main__":
    main()