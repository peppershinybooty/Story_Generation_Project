import os
import shutil

# Directories to clean
DIRS_TO_CLEAN = ["./characters", "./world", "./data", "./backups"]  # Add other folders if needed

def clean_directories(directories):
    for directory in directories:
        if os.path.exists(directory):
            # Clear the directory but keep the folder itself
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)  # Delete file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Delete sub-directory
            print(f"Cleaned {directory}")
        else:
            print(f"Directory {directory} does not exist!")

# Execute Cleaning
clean_directories(DIRS_TO_CLEAN)