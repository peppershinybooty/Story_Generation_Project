import os
import shutil
from datetime import datetime

BACKUP_FOLDER = "backups"

def ensure_backup_folder():
    """Create backup folder if it doesn't exist"""
    if not os.path.exists(BACKUP_FOLDER):
        os.makedirs(BACKUP_FOLDER)
        print(f"Created backup folder: {BACKUP_FOLDER}/")

def backup_file(filepath):
    """
    Create timestamped backup of a file before modification.
    Returns path to backup file, or None if file doesn't exist.
    """
    if not os.path.exists(filepath):
        return None
    
    ensure_backup_folder()
    
    # Get filename without path
    filename = os.path.basename(filepath)
    name_without_ext = os.path.splitext(filename)[0]
    
    # Create readable, sortable timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    backup_filename = f"{name_without_ext}_backup_{timestamp}.txt"
    backup_path = os.path.join(BACKUP_FOLDER, backup_filename)
    
    # Copy file to backup
    shutil.copy2(filepath, backup_path)
    print(f"✓ Backed up: {filename} -> {backup_filename}")
    
    return backup_path

def backup_multiple(filepaths):
    """
    Backup multiple files at once.
    Returns list of backup paths.
    """
    backups = []
    for filepath in filepaths:
        backup_path = backup_file(filepath)
        if backup_path:
            backups.append(backup_path)
    return backups