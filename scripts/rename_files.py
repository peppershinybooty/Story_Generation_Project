import os

# Base Path for Character Files
CHARACTERS_FOLDER = "characters"  # No `./`, cleaner to read

# Ensure directory always exists
os.makedirs(CHARACTERS_FOLDER, exist_ok=True)  # Create if missing

def rename_files(directory):
    for filename in os.listdir(directory):
        old_path = os.path.join(directory, filename)

        # Skip directories, process only files
        if os.path.isdir(old_path):
            continue

        # Rename logic
        if "background" in filename.lower():
            new_name = f"character_{filename.split('_')[1]}_background.txt"
        elif "shortterm" in filename.lower():
            new_name = f"character_{filename.split('_')[1]}_shortterm.txt"
        elif "longterm" in filename.lower():
            new_name = f"character_{filename.split('_')[1]}_longterm.txt"
        else:
            print(f"Skipping file '{filename}', unknown naming convention.")
            continue

        new_path = os.path.join(directory, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed {filename} -> {new_name}")

# Execute Renaming
rename_files(CHARACTERS_FOLDER)