



import argparse
import logging
import os
import shutil
import time
import hashlib
from logging.handlers import RotatingFileHandler

# Parse command line arguments
parser = argparse.ArgumentParser(description="Synchronize two folders.")
parser.add_argument("source", help="Source folder path")
parser.add_argument("replica", help="Replica folder path")
parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
parser.add_argument("log_file", help="Path to the log file")
args = parser.parse_args()

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        RotatingFileHandler(args.log_file, maxBytes=5*1024*1024, backupCount=2),
                        logging.StreamHandler()
                    ])

# Function to calculate file MD5
def file_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Function to synchronize folders
def sync_folders(source, replica):
    # Ensure trailing slash for correct path replacement
    source = os.path.join(source, '')
    replica = os.path.join(replica, '')

    # Copy or update files from source to replica
    for root, dirs, files in os.walk(source):
        replica_root = root.replace(source, replica)
        if not os.path.exists(replica_root):
            os.makedirs(replica_root)
            logging.info(f"Directory created: {replica_root}")

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)
            if not os.path.exists(replica_file) or file_md5(source_file) != file_md5(replica_file):
                logging.info(f"Copying: {source_file} to {replica_file}")
                shutil.copy2(source_file, replica_file)

    # Remove files and directories no longer present in source
    for root, dirs, files in os.walk(replica, topdown=False):
        source_root = root.replace(replica, source)
        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)
            if not os.path.exists(source_file):
                logging.info(f"Removing: {replica_file}")
                os.remove(replica_file)
        for dir in dirs:
            replica_dir = os.path.join(root, dir)
            if not os.listdir(replica_dir):
                logging.info(f"Removing directory: {replica_dir}")
                os.rmdir(replica_dir)

# Main loop to run synchronization periodically
if __name__ == "__main__":
    while True:
        logging.info("Starting synchronization")
        sync_folders(args.source, args.replica)
        logging.info("Synchronization complete. Waiting for the next interval.")
        time.sleep(args.interval)


