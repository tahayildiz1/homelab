import os
import hashlib
from virustotal_python import Virustotal

# Enter your VirusTotal API key here
api_key = "YOUR_API_KEY"

# Function to calculate the SHA256 hash of a file
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as file:
        while chunk := file.read(8192):
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()

# Function to check a file using the VirusTotal API
def check_file_virustotal(file_path, vt_client):
    file_hash = calculate_sha256(file_path)
    response = vt_client.request_file_report(file_hash)

    if response["results"]["response_code"] == 1:
        # File is in VirusTotal database
        if response["results"]["positives"] > 0:
            # File is detected as malicious, delete it
            print(f"File '{file_path}' is detected as malicious. Deleting...")
            os.remove(file_path)
        else:
            # File is safe
            print(f"File '{file_path}' is safe.")
    else:
        print(f"File '{file_path}' is not in the VirusTotal database.")

# Function to scan the Downloads folder
def scan_downloads_folder():
    vt_client = Virustotal(API_KEY=api_key)
    downloads_path = os.path.expanduser("~\\Downloads")

    for root, dirs, files in os.walk(downloads_path):
        for file in files:
            file_path = os.path.join(root, file)
            check_file_virustotal(file_path, vt_client)

if __name__ == "__main__":
    scan_downloads_folder()
