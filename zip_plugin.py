import os
import zipfile
from pathlib import Path

def create_zip(source_dir, output_filename):
    # The root folder inside the zip should be 'capi-gateway'
    root_folder_name = os.path.basename(os.path.normpath(source_dir))
    
    output_path = Path(output_filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Determine the relative path to keep the directory structure
                rel_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                # Ensure forward slashes for cross-platform compatibility (Linux servers)
                zip_path = rel_path.replace(os.sep, '/')
                zipf.write(file_path, zip_path)
                print(f"Added: {zip_path}")

project_root = Path(__file__).resolve().parent
source_directory = project_root / "wordpress-plugin" / "capi-gateway"
output_zips = [
    project_root / "wordpress-plugin" / "capi-gateway.zip",
    project_root / "capi-gateway-updated.zip",
]

for output_zip in output_zips:
    create_zip(source_directory, output_zip)
    print(f"\nSuccessfully created: {output_zip}")
