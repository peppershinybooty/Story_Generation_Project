import os
import requests
from backup_utils import backup_file

# Configuration
API_URL = "http://127.0.0.1:5000/v1/chat/completions"

# Get script directory and project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

# File paths relative to project root
CHARACTER_FOLDER = os.path.join(PROJECT_ROOT, "characters")
WORLD_FOLDER = os.path.join(PROJECT_ROOT, "world")
STORY_FOLDER = os.path.join(PROJECT_ROOT, "story")
STORY_FILE = os.path.join(STORY_FOLDER, "story_recent.txt")

def load_file(filepath):
    """Load text file, return content or empty string"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding='utf-8') as f:
            return f.read()
    return ""

def get_ai_response(context, max_tokens=800):
    """Call Oobabooga API using chat completions format"""
    payload = {
        "mode": "instruct",
        "messages": [{"role": "user", "content": context}],
        "max_tokens": max_tokens,
        "temperature": 0.8,
        "top_p": 0.9
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
        return None

def get_protagonist_input():
    """Get protagonist paragraph from user"""
    print("\n[YOUR TURN - Write protagonist's paragraph]")
    print("(Press Enter twice when done)\n")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)

def show_main_menu():
    """Display main options menu"""
    print("\n=== OPTIONS ===")
    print("[1] Accept - continue writing")
    print("[2] Regenerate - see submenu")
    print("[3] Edit manually - paste your version")
    print("[4] Commit scene - save and exit")
    return input("Choose: ").strip()

def show_regen_menu():
    """Display regeneration submenu"""
    print("\n=== REGENERATE OPTIONS ===")
    print("[a] Fresh regeneration - completely new response")
    print("[b] Major redirect - big structural/action changes")
    print("[c] Minor adjustment - small tone/detail tweaks")
    print("[d] Remind of detail - inject forgotten context/fact")
    return input("Choose: ").strip().lower()

def interactive_scene():
    """Main interactive scene writing loop"""
    
    # Get NPCs for this scene
    npcs_input = input("Characters in this scene (comma-separated): ").strip()
    npcs = [npc.strip() for npc in npcs_input.split(",")]
    
    # Load world/style context once
    print("\nLoading context...")
    style_guide = load_file(f"{WORLD_FOLDER}/style_guide.txt")
    world_state = load_file(f"{WORLD_FOLDER}/world_state.txt")
    world_encyclopedic = load_file(f"{WORLD_FOLDER}/world_encyclopedic.txt")
    story_recent = load_file(STORY_FILE)
    
    # Load NPC data
    npc_data = {}
    for npc in npcs:
        npc_clean = npc.lower().replace(" ", "_")
        background = load_file(f"{CHARACTER_FOLDER}/character_{npc_clean}_background.txt")
        shortterm = load_file(f"{CHARACTER_FOLDER}/character_{npc_clean}_shortterm.txt")
        longterm = load_file(f"{CHARACTER_FOLDER}/character_{npc_clean}_longterm.txt")
        
        if not background and not shortterm and not longterm:
            print(f"Warning: No files found for '{npc}' - skipping")
            continue
            
        npc_data[npc_clean] = {
            'name': npc,
            'background': background,
            'shortterm': shortterm,
            'longterm': longterm
        }
    
    if not npc_data:
        print("Error: No valid NPCs loaded. Exiting.")
        return
    
    # Scene draft accumulator
    scene_draft = []
    
    print("\n=== INTERACTIVE SCENE MODE ===\n")
    
    # Main writing loop
    while True:
        # Get protagonist's paragraph
        protag_paragraph = get_protagonist_input()
        
        if not protag_paragraph.strip():
            print("Empty input. Ending scene.")
            break
        
        # Build base context for AI
        npc_context_parts = []
        for npc_key, data in npc_data.items():
            npc_section = f"CHARACTER [{data['name'].upper()}]:\n"
            if data['background']:
                npc_section += f"BACKGROUND:\n{data['background']}\n\n"
            if data['shortterm']:
                npc_section += f"SHORT-TERM MEMORY:\n{data['shortterm']}\n\n"
            if data['longterm']:
                npc_section += f"LONG-TERM MEMORY:\n{data['longterm']}\n"
            npc_context_parts.append(npc_section)
        
        npc_context = "\n".join(npc_context_parts)
        current_draft = "\n\n".join(scene_draft)
        
        base_context = f"""{style_guide}

WORLD ENCYCLOPEDIA:
{world_encyclopedic}

CURRENT WORLD STATE:
{world_state}

ACTIVE CHARACTERS:
{npc_context}

RECENT STORY:
{story_recent}

CURRENT SCENE SO FAR:
{current_draft}

LATEST ACTION:
{protag_paragraph}

Continue the scene. How do the NPCs react?"""
        
        # AI generation loop with regeneration options
        additional_instruction = ""
        
        while True:
            # Build full context with any additional instructions
            full_context = base_context
            if additional_instruction:
                full_context += f"\n\n{additional_instruction}"
            
            # DEBUG: Show what's being loaded
            print("\n=== CONTEXT DEBUG ===")
            print(f"NPCs loaded: {', '.join([data['name'] for data in npc_data.values()])}")
            for npc_key, data in npc_data.items():
                bg_lines = len([l for l in data['background'].split('\n') if l.strip()]) if data['background'] else 0
                st_lines = len([l for l in data['shortterm'].split('\n') if l.strip()]) if data['shortterm'] else 0
                lt_lines = len([l for l in data['longterm'].split('\n') if l.strip()]) if data['longterm'] else 0
                print(f"  {data['name']}: BG={bg_lines} lines, ST={st_lines} entries, LT={lt_lines} entries")
            
            draft_paragraphs = len(scene_draft)
            print(f"Scene draft: {draft_paragraphs} paragraphs")
            print(f"Style guide: {'loaded' if style_guide else 'MISSING'}")
            print(f"World state: {'loaded' if world_state else 'MISSING'}")
            print("====================\n")
            
            # Generate AI response
            print("Generating AI response...")
            ai_response = get_ai_response(full_context)
            
            if not ai_response:
                print("Generation failed. Try again.")
                retry = input("Retry? (y/n): ").strip().lower()
                if retry != 'y':
                    break
                continue
            
            # Show response
            print("\n" + "="*60)
            print("AI RESPONSE:")
            print("="*60)
            print(ai_response)
            print("="*60)
            
            # Get user choice
            choice = show_main_menu()
            
            if choice == "1":  # Accept
                scene_draft.append(protag_paragraph)
                scene_draft.append(ai_response)
                print("\n✓ Added to scene draft.")
                break
            
            elif choice == "2":  # Regenerate
                regen_choice = show_regen_menu()
                
                if regen_choice == "a":  # Fresh
                    print("\nRegenerating fresh response...")
                    additional_instruction = ""
                    continue
                
                elif regen_choice == "b":  # Major redirect
                    redirect = input("\nDescribe major change needed: ").strip()
                    if redirect:
                        additional_instruction = f"MAJOR CHANGE REQUIRED: {redirect}"
                        print("\nRegenerating with major redirect...")
                        continue
                    else:
                        print("No change specified. Regenerating fresh...")
                        additional_instruction = ""
                        continue
                
                elif regen_choice == "c":  # Minor adjustment
                    adjustment = input("\nDescribe minor adjustment: ").strip()
                    if adjustment:
                        additional_instruction = f"MINOR ADJUSTMENT NEEDED: {adjustment}"
                        print("\nRegenerating with adjustment...")
                        continue
                    else:
                        print("No adjustment specified. Regenerating fresh...")
                        additional_instruction = ""
                        continue
                
                elif regen_choice == "d":  # Remind of detail
                    reminder = input("\nWhat detail should AI remember?: ").strip()
                    if reminder:
                        additional_instruction = f"IMPORTANT CONTEXT TO REMEMBER: {reminder}"
                        print("\nRegenerating with reminder...")
                        continue
                    else:
                        print("No reminder specified. Regenerating fresh...")
                        additional_instruction = ""
                        continue
                
                else:
                    print("Invalid choice. Regenerating fresh...")
                    additional_instruction = ""
                    continue
            
            elif choice == "3":  # Edit manually
                print("\nPaste your edited version (Press Enter twice when done):\n")
                edited_lines = []
                while True:
                    line = input()
                    if line == "":
                        break
                    edited_lines.append(line)
                
                if edited_lines:
                    ai_response = "\n".join(edited_lines)
                    scene_draft.append(protag_paragraph)
                    scene_draft.append(ai_response)
                    print("\n✓ Edited version added to draft.")
                    break
                else:
                    print("No input received. Returning to options...")
                    continue
            
            elif choice == "4":  # Commit scene
                scene_draft.append(protag_paragraph)
                scene_draft.append(ai_response)
                
                # Save scene
                final_scene = "\n\n".join(scene_draft)
                
                print("\n" + "="*60)
                print("FINAL SCENE:")
                print("="*60)
                print(final_scene)
                print("="*60)
                
                confirm = input("\nCommit this scene? (y/n): ").strip().lower()
                if confirm == 'y':
                    backup_file(STORY_FILE)
                    
                    with open(STORY_FILE, "a", encoding="utf-8") as f:
                        f.write(f"\n\n{final_scene}")
                    
                    print(f"\n✓ Scene committed to {STORY_FILE}")
                    print("\nREMINDER: Run batch_generate_memories.py to update character memories.")
                    return
                else:
                    print("Commit cancelled. Returning to options...")
                    continue
            
            else:
                print("Invalid choice. Try again.")
                continue
        
        # Ask if user wants to continue scene
        continue_writing = input("\nContinue writing this scene? (y/n): ").strip().lower()
        if continue_writing != 'y':
            print("\nScene incomplete. Progress not saved.")
            break

def main():
    print("="*60)
    print("INTERACTIVE SCENE WRITER")
    print("="*60)
    interactive_scene()

if __name__ == "__main__":
    main()