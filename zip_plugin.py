import os
import zipfile

def create_zip(source_dir, output_filename):
    # The root folder inside the zip should be 'capi-gateway'
    root_folder_name = os.path.basename(os.path.normpath(source_dir))
    
    with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                # Determine the relative path to keep the directory structure
                rel_path = os.path.relpath(file_path, os.path.dirname(source_dir))
                # Ensure forward slashes for cross-platform compatibility (Linux servers)
                zip_path = rel_path.replace(os.sep, '/')
                zipf.write(file_path, zip_path)
                print(f"Added: {zip_path}")

source_directory = r"c:\Users\Hridoy Hossain\Desktop\Server site traking\wordpress-plugin\capi-gateway"
output_zip = r"c:\Users\Hridoy Hossain\Desktop\Server site traking\capi-gateway-updated.zip"

create_zip(source_directory, output_zip)
print(f"\nSuccessfully created: {output_zip}")
