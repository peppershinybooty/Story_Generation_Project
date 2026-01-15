import os

# Define where character files will go
CHARACTER_FOLDER = "characters"

# Function to create a new character
def create_character(character_name):
    # Ensure the `characters` folder exists
    os.makedirs(CHARACTER_FOLDER, exist_ok=True)

    # Build file paths for the new character
    background_path = os.path.join(CHARACTER_FOLDER, f"character_{character_name}_background.txt")
    shortterm_path = os.path.join(CHARACTER_FOLDER, f"character_{character_name}_shortterm.txt")
    longterm_path = os.path.join(CHARACTER_FOLDER, f"character_{character_name}_longterm.txt")

    # Write default content into each file
    with open(background_path, "w") as bg:
        bg.write(f"[Background for {character_name}]\n")
    with open(shortterm_path, "w") as st:
        st.write(f"[Short-term memories for {character_name}]\n")
    with open(longterm_path, "w") as lt:
        lt.write(f"[Long-term memories for {character_name}]\n")

    print(f"Character files created for: {character_name}")

# Prompt the user for a character name
if __name__ == "__main__":
    char_name = input("Enter new character name: ").strip().replace(" ", "_").lower()
    create_character(char_name)