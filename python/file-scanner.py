import os
import hashlib
import requests

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
def check_file_virustotal(file_path):
    file_hash = calculate_sha256(file_path)
    url = f"https://www.virustotal.com/vtapi/v2/file/report?apikey={api_key}&resource={file_hash}"

    response = requests.get(url)
    
    if response.status_code == 200:
        result = response.json()
        
        if result["response_code"] == 1:
            # File is in VirusTotal database
            if result["positives"] > 0:
                # File is detected as malicious, delete it
                print(f"File '{file_path}' is detected as malicious. Deleting...")
                os.remove(file_path)
            else:
                # File is safe
                print(f"File '{file_path}' is safe.")
        else:
            print(f"File '{file_path}' is not in the VirusTotal database.")
    else:
        print(f"Error checking file '{file_path}' with VirusTotal API.")

# Function to scan the Downloads folder
def scan_downloads_folder():
    downloads_path = os.path.expanduser("~\\Downloads")

    for root, dirs, files in os.walk(downloads_path):
        for file in files:
            file_path = os.path.join(root, file)
            check_file_virustotal(file_path)

if __name__ == "__main__":
    scan_downloads_folder()
