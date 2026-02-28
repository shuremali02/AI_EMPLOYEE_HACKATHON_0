import argparse
import os
import shutil
import sys

def move_task(source, destination):
    # Define base vault path
    base_path = "AI_Employee_Vault"

    # Construct full paths
    source_path = os.path.join(base_path, source)
    dest_path = os.path.join(base_path, destination)

    # Validate that paths are within allowed directories
    allowed_dirs = ["Inbox", "Needs_Action", "Done", "Needs_Approval"]
    source_dir = source.split("/")[0] if "/" in source else source
    dest_dir = destination.split("/")[0] if "/" in destination else destination

    if source_dir not in allowed_dirs or dest_dir not in allowed_dirs:
        print(f"Error: Invalid directory. Only {allowed_dirs} are allowed.")
        sys.exit(1)

    try:
        # Check if source file exists
        if not os.path.exists(source_path):
            print(f"Error: Source file does not exist: {source_path}")
            sys.exit(1)

        # Create destination directory if it doesn't exist
        dest_dir_path = os.path.dirname(dest_path)
        os.makedirs(dest_dir_path, exist_ok=True)

        # Move the file
        shutil.move(source_path, dest_path)

        print(f"File moved successfully from {source} to {destination}")

    except Exception as e:
        print(f"Failed to move file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Move task files between vault directories")
    parser.add_argument("--source", required=True, help="Source file path (e.g., Inbox/filename.md)")
    parser.add_argument("--destination", required=True, help="Destination file path (e.g., Needs_Action/filename.md)")

    args = parser.parse_args()

    move_task(args.source, args.destination)