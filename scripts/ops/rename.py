import os
import glob
import shutil

project_root = r"c:\Users\Hridoy Hossain\Desktop\Server site traking"

replacements = {
    "Buykori AdSync": "Buykori AdSync",
    "buykori-adsync": "buykori-adsync",
    "Buykori-AdSync": "Buykori-AdSync",
    "buykori_adsync": "buykori_adsync"
}

# Directories to skip
skip_dirs = {".git", ".pytest_cache", "venv", "__pycache__", "alembic"}

def replace_in_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return False

    new_content = content
    for old_str, new_str in replacements.items():
        new_content = new_content.replace(old_str, new_str)

    if new_content != content:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    return False

# 1. Replace strings in files
changed_files = []
for root, dirs, files in os.walk(project_root):
    dirs[:] = [d for d in dirs if d not in skip_dirs]
    for file in files:
        if file.endswith((".py", ".md", ".php", ".html", ".js", ".css", ".env", ".txt")):
            filepath = os.path.join(root, file)
            if replace_in_file(filepath):
                changed_files.append(filepath)

print(f"Updated {len(changed_files)} files.")

# 2. Rename directories and files
plugin_dir = os.path.join(project_root, "wordpress-plugin")
old_plugin_folder = os.path.join(plugin_dir, "buykori-adsync")
new_plugin_folder = os.path.join(plugin_dir, "buykori-adsync")

if os.path.exists(old_plugin_folder):
    os.rename(old_plugin_folder, new_plugin_folder)
    print(f"Renamed {old_plugin_folder} to {new_plugin_folder}")

old_plugin_file = os.path.join(new_plugin_folder, "buykori-adsync.php")
new_plugin_file = os.path.join(new_plugin_folder, "buykori-adsync.php")

if os.path.exists(old_plugin_file):
    os.rename(old_plugin_file, new_plugin_file)
    print(f"Renamed {old_plugin_file} to {new_plugin_file}")

# 3. Rename zip files if they exist
old_zip = os.path.join(project_root, "buykori-adsync-updated.zip")
new_zip = os.path.join(project_root, "buykori-adsync-updated.zip")
if os.path.exists(old_zip):
    os.rename(old_zip, new_zip)
    print("Renamed buykori-adsync-updated.zip")

print("Done renaming!")
