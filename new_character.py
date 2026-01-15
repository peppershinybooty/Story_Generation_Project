import os

def create_character_files(character_name, role, race_age, description, personality, backstory, skills, relationships):
    """Create the 3 memory files for a new character"""
    
    char_lower = character_name.lower().replace(" ", "_")
    
    # Background file
    background_content = f"""CHARACTER: {character_name}
ROLE: {role}
RACE/AGE: {race_age}

PHYSICAL DESCRIPTION:
{description}

PERSONALITY CORE:
{personality}

BACKSTORY (BEFORE STORY BEGAN):
{backstory}

SKILLS/CAPABILITIES:
{skills}

RELATIONSHIPS (STARTING):
{relationships}
"""
    
    # Short-term memory file
    shortterm_content = f"""CHARACTER: {character_name}
SHORT-TERM MEMORY (Recent detailed memories - last 10 scenes):

[This file starts empty. The memory script will add entries here after each scene.]
"""
    
    # Long-term memory file
    longterm_content = f"""CHARACTER: {character_name}
LONG-TERM MEMORY (Consolidated summaries):

[This file starts empty. Consolidated summaries will be added here.]
"""
    
    # Write files
    with open(f"character_{char_lower}_background.txt", 'w', encoding='utf-8') as f:
        f.write(background_content)
    
    with open(f"character_{char_lower}_shortterm.txt", 'w', encoding='utf-8') as f:
        f.write(shortterm_content)
    
    with open(f"character_{char_lower}_longterm.txt", 'w', encoding='utf-8') as f:
        f.write(longterm_content)
    
    print(f"\n✓ Created 3 files for {character_name}")
    print(f"  - character_{char_lower}_background.txt")
    print(f"  - character_{char_lower}_shortterm.txt")
    print(f"  - character_{char_lower}_longterm.txt")

def main():
    print("=== CREATE NEW CHARACTER ===\n")
    
    name = input("Character name: ")
    role = input("Role/title: ")
    race_age = input("Race/age: ")
    
    print("\nPhysical description (press Enter twice when done):")
    desc_lines = []
    while True:
        line = input()
        if line == "" and desc_lines and desc_lines[-1] == "":
            break
        desc_lines.append(line)
    description = "\n".join(desc_lines[:-1])
    
    print("\nPersonality core (bullet points, press Enter twice when done):")
    pers_lines = []
    while True:
        line = input()
        if line == "" and pers_lines and pers_lines[-1] == "":
            break
        pers_lines.append(line)
    personality = "\n".join(pers_lines[:-1])
    
    print("\nBackstory before story began (press Enter twice when done):")
    back_lines = []
    while True:
        line = input()
        if line == "" and back_lines and back_lines[-1] == "":
            break
        back_lines.append(line)
    backstory = "\n".join(back_lines[:-1])
    
    print("\nSkills/capabilities:")
    skills = input()
    
    print("\nStarting relationships with other characters (press Enter twice when done):")
    rel_lines = []
    while True:
        line = input()
        if line == "" and rel_lines and rel_lines[-1] == "":
            break
        rel_lines.append(line)
    relationships = "\n".join(rel_lines[:-1])
    
    create_character_files(name, role, race_age, description, personality, backstory, skills, relationships)
    
    another = input("\nCreate another character? (y/n): ").lower()
    if another == 'y':
        main()

if __name__ == "__main__":
    main()