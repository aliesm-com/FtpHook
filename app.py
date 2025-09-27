import requests
import os
import re
from typing import Optional, Dict, Any
import json
from ftplib import FTP
from dotenv import load_dotenv
import shutil  # Add this import for directory removal
from flask import Flask, request, jsonify

load_dotenv()


class GitHubReleaseDownloader:
    """
    Class for downloading the latest release from GitHub
    """
    
    def __init__(self, repo_name: str, token: Optional[str] = None):
        """
        Initialize the downloader
        
        Args:
            repo_name (str): Repository name in format "owner/repo"
            token (str, optional): GitHub token for accessing private repositories
        """
        self.repo_name = repo_name
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Release-Downloader",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        if self.token:
            self.headers["Authorization"] = f"Bearer {self.token}"
    
    def get_latest_release(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the latest release
        
        Returns:
            Dict: Release information or None if error
        """
        url = f"{self.base_url}/repos/{self.repo_name}/releases/latest"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error getting release information: {e}")
            return None
    
    def find_release_asset(self, release_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Find file with pattern release-*.tar.gz
        
        Args:
            release_data (Dict): Release information
            
        Returns:
            Dict: File information or None
        """
        assets = release_data.get("assets", [])
        pattern = re.compile(r"^release-.*\.tar\.gz$")

        for asset in assets:
            if pattern.match(asset["name"]):
                return asset
        
        print("No file found with pattern release-*.tar.gz")
        return None
    
    def download_file(self, download_url: str, filename: str, download_path: str = "./downloads", use_api_url: bool = False) -> bool:
        """
        Download file
        
        Args:
            download_url (str): Download URL or API asset URL
            filename (str): File name
            download_path (str): Save path
            use_api_url (bool): Whether to use the API asset URL for authenticated download
            
        Returns:
            bool: True if successful, False if error
        """
        # Create download folder if it doesn't exist
        os.makedirs(download_path, exist_ok=True)
        
        file_path = os.path.join(download_path, filename)
        
        try:
            print(f"Starting download: {filename}")
            
            headers = self.headers.copy()
            if use_api_url:
                headers["Accept"] = "application/octet-stream"
            
            with requests.get(download_url, headers=headers, stream=True) as response:
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded_size = 0
                
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)
                            downloaded_size += len(chunk)
                            
                            # Show download progress
                            if total_size > 0:
                                progress = (downloaded_size / total_size) * 100
                                print(f"\rProgress: {progress:.1f}%%", end="")
            
            print(f"\nDownload completed successfully: {file_path}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def extract_file(self, file_path: str, extract_to: str) -> bool:
        """
        Extract a .tar.gz file to a specified directory

        Args:
            file_path (str): Path to the .tar.gz file
            extract_to (str): Directory to extract the contents to

        Returns:
            bool: True if extraction is successful, False otherwise
        """
        import tarfile

        try:
            print(f"Extracting {file_path} to {extract_to}")
            with tarfile.open(file_path, "r:gz") as tar:
                tar.extractall(path=extract_to)
            print(f"Extraction completed successfully: {extract_to}")
            return True
        except Exception as e:
            print(f"Error extracting file: {e}")
            return False

    def download_latest_release(self, download_path: str = "./downloads") -> bool:
        """
        Download the latest release
        
        Args:
            download_path (str): File save path
            
        Returns:
            bool: True if successful
        """
        print(f"Getting latest release information for: {self.repo_name}")
        
        # Get release information
        release_data = self.get_latest_release()
        if not release_data:
            return False
        
        print(f"Latest release: {release_data['tag_name']} - {release_data['name']}")
        
        # Find the target file
        asset = self.find_release_asset(release_data)
        if not asset:
            return False
        
        print(f"File found: {asset['name']} ({asset['size']} bytes)")
        
        # Use the asset `url` for authenticated download
        return self.download_file(
            asset["url"],
            asset["name"],
            download_path,
            use_api_url=True
        )

    def download_and_extract_latest_release(self, download_path: str = "./downloads") -> bool:
        """
        Download and extract the latest release

        Args:
            download_path (str): Directory to save and extract the file

        Returns:
            bool: True if successful, False otherwise
        """
        # Download the latest release
        if not self.download_latest_release(download_path):
            return False

        # Determine the file path and extraction directory
        file_name = self.find_release_asset(self.get_latest_release())["name"]
        file_path = os.path.join(download_path, file_name)
        extract_to = os.path.join(download_path, file_name.replace(".tar.gz", ""))

        # Extract the file
        return self.extract_file(file_path, extract_to)

    def upload_to_ftp(self, local_path: str, remote_path: str) -> bool:
        """
        Upload files to an FTP server

        Args:
            local_path (str): Path to the local directory to upload
            remote_path (str): Path to the remote directory on the FTP server

        Returns:
            bool: True if upload is successful, False otherwise
        """
        # Load environment variables
        

        ftp_host = os.getenv("FTP_HOST")
        ftp_user = os.getenv("FTP_USER")
        ftp_password = os.getenv("FTP_PASSWORD")

        if not all([ftp_host, ftp_user, ftp_password]):
            print("FTP credentials are missing in the .env file.")
            return False

        try:
            print(f"Connecting to FTP server: {ftp_host}")
            ftp = FTP(ftp_host)
            ftp.login(ftp_user, ftp_password)

            # Ensure the remote directory exists
            try:
                ftp.cwd(remote_path)
            except Exception:
                print(f"Creating remote directory: {remote_path}")
                ftp.mkd(remote_path)
                ftp.cwd(remote_path)

            # Upload files
            for root, dirs, files in os.walk(local_path):
                for dirname in dirs:
                    dir_path = os.path.relpath(os.path.join(root, dirname), local_path).replace("\\", "/")
                    print(dir_path)
                    try:
                        ftp.mkd(dir_path)
                    except Exception as e:
                        print(f"{e}")

                for filename in files:
                    file_path = os.path.join(root, filename)
                    # Ensure paths use forward slashes
                    remote_file_path = os.path.relpath(file_path, local_path).replace("\\", "/")
                    print(f"Uploading {file_path} to {remote_file_path}")
                    with open(file_path, "rb") as file:
                        ftp.storbinary(f"STOR {remote_file_path}", file)

            ftp.quit()
            print("Upload completed successfully.")
            return True

        except Exception as e:
            print(f"Error uploading to FTP: {e}")
            return False

    def download_extract_and_upload(self, download_path: str = "./downloads", remote_path: str = None) -> bool:
        """
        Download, extract, and upload the latest release to an FTP server

        Args:
            download_path (str): Directory to save and extract the file
            remote_path (str): Remote directory on the FTP server

        Returns:
            bool: True if all steps are successful, False otherwise
        """
        # Download and extract the latest release
        if not self.download_and_extract_latest_release(download_path):
            return False

        # Prompt user for remote directory if not provided
        if not remote_path:
            remote_path = input("Enter the remote directory on the FTP server: ")

        # Determine the extraction directory
        file_name = self.find_release_asset(self.get_latest_release())["name"]
        extract_to = os.path.join(download_path, file_name.replace(".tar.gz", ""))

        # Upload to FTP
        success = self.upload_to_ftp(extract_to, remote_path)

        # Remove the tar.gz file and extracted directory after successful upload
        if success:
            # Determine the file path and extraction directory
            file_path = os.path.join(download_path, file_name)
            
            # Remove the tar.gz file
            try:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")

            # Remove the extracted directory
            try:
                shutil.rmtree(extract_to)
                print(f"Deleted directory: {extract_to}")
            except Exception as e:
                print(f"Error deleting directory {extract_to}: {e}")

        return success


app = Flask(__name__)

@app.route('/download-extract-upload', methods=['POST'])
def download_extract_upload():
    if not data.get('api_key') or data.get('api_key') != os.getenv('APIKEY'):
        return jsonify({'error': 'API key is invalid or missing'}), 403
    data = request.json
    download_path = './downloads'
    github_token = os.getenv('GITHUB_TOKEN')
    repo_name = data.get('repo_name')
    remote_path = data.get('remote_path')

    if not repo_name or not github_token or not remote_path:
        return jsonify({'error': 'repo_name, github_token, and remote_path are required'}), 400

    downloader = GitHubReleaseDownloader(repo_name, github_token)
    success = downloader.download_extract_and_upload(download_path, remote_path)

    if success:
        return jsonify({'message': 'Download, extraction, and upload completed successfully'}), 200
    else:
        return jsonify({'error': 'Operation failed'}), 500

if __name__ == '__main__':
    app.run(debug=True)
