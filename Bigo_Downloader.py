import subprocess
import json
import sys
import requests
import re
from datetime import datetime

def get_available_streams(url):
    """
    Fetch available streams from Streamlink in JSON format.
    Returns a dict of available qualities.
    """
    try:
        result = subprocess.run(
            ['streamlink', '--json', url],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(result.stdout)
        return data.get('streams', {})
    except subprocess.CalledProcessError as e:
        print(f"Error fetching streams: {e}")
        print("Ensure Streamlink is installed and the URL is valid (stream must be live).")
        return {}
    except json.JSONDecodeError:
        print("Error parsing Streamlink output.")
        return {}

def download_stream(url, quality, output_file='bigo_download.mp4'):
    """
    Download the selected stream quality to output_file.
    """
    try:
        subprocess.run(
            ['streamlink', url, quality, '-o', output_file],
            check=True
        )
        print(f"Download completed: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Download failed: {e}")
        return False

def fetch_streamer_info(url):
    """
    Fetch streamer ID and name from the BIGO URL.
    """
    # Parse ID from URL
    id_match = re.search(r'/(\d+)', url)
    streamer_id = id_match.group(1) if id_match else 'unknown'
    
    # Fetch page to get name from title
    streamer_name = 'unknown'
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        title_match = re.search(r'^(.*?) - BIGO LIVE', response.text, re.IGNORECASE)
        if title_match:
            streamer_name = re.sub(r'[<>:"/\\|?*]', '_', title_match.group(1).strip())  # Sanitize for filename
    except Exception as e:
        print(f"Warning: Could not fetch streamer name: {e}")
    
    # Download date
    download_date = datetime.now().strftime('%Y%m%d')
    
    return streamer_id, streamer_name, download_date

def main():
    while True:
        url = input("Enter the BIGO.tv URL (e.g., https://www.bigo.tv/738263354) or 'q' to quit: ").strip()
        if url.lower() == 'q':
            print("Goodbye!")
            break
        if not url:
            print("No URL provided. Try again.")
            continue
        
        # Fetch streamer info
        streamer_id, streamer_name, download_date = fetch_streamer_info(url)
        print(f"Streamer ID: {streamer_id}, Name: {streamer_name}")
        
        streams = get_available_streams(url)
        
        if not streams:
            print("No streams available. Check if the stream is live and try again.")
            continue
        
        quality = 'best'  # Auto-select best quality
        
        default_filename = f'{streamer_id}_{streamer_name}_{download_date}.mp4'
        output_file = input(f"Enter output filename (default: {default_filename}): ").strip() or default_filename
        
        print(f"\nDownloading best quality to {output_file}...")
        if download_stream(url, quality, output_file):
            print("Success!")
        else:
            print("Failed. Try again.")
        
        again = input("\nDownload another? (y/n): ").strip().lower()
        if again != 'y':
            break

if __name__ == "__main__":
    main()
