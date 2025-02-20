import os
import shutil
import sys

def distribute_files(source_dir, dira):
    # Create target directories if they don't exist
    os.makedirs(dira, exist_ok=True)

    # Get a list of all files in the source directory
    files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f))]

    # Counters for the batch
    count = 0
    batch_size = 10

    # Loop through and distribute files
    for file in files:
        source_path = os.path.join(source_dir, file)
        if count < 8:
            pass
        else:
            shutil.copy(source_path, dira)  # Move file to dirb

        # Increment and reset counter
        count = (count + 1) % batch_size

    print(f"Files have been distributed into '{dira}' and '{dira}'!")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python distribute_files.py <source_dir> <dira> <dira>")
        sys.exit(1)

    source_dir = sys.argv[1]
    dira = sys.argv[2]

    if not os.path.isdir(source_dir):
        print(f"Error: '{source_dir}' is not a valid directory.")
        sys.exit(1)

    distribute_files(source_dir, dira)
