import os
import time
import sys
import os.path
from pathlib import Path
from datetime import datetime

from atproto import Client
from dotenv import load_dotenv
from get_tweet_data import get_tweet_data  # Assuming this returns frame_filepath and post_text

# Config and Env
load_dotenv()
frame_dir = f"/media/sf_Framebot/Veep2"
# Bluesky credentials
BLUESKY_HANDLE = os.getenv('BLUESKY_HANDLE')
BLUESKY_PASSWORD = os.getenv('BLUESKY_PASSWORD')
print(BLUESKY_HANDLE, BLUESKY_PASSWORD)
# Timing
wait_time = 600  # Seconds after a post, 30 minutes by default

# Initialize Bluesky client
client = Client()

try:
    # Log in to Bluesky
    client.login(BLUESKY_HANDLE, BLUESKY_PASSWORD)
    print(f"Logged in to Bluesky as: {BLUESKY_HANDLE}")
except Exception as e:
    print(f"Error logging in to Bluesky: {e}")
    sys.exit()

# Load the index from a file (or initialize it to 0 if the file doesn't exist)
index_file = "progress.txt"
if os.path.exists(index_file):
    with open(index_file) as f:
        frames_posted = int(f.read().strip())
    print("Progress.txt found. Resuming...")
else:
    frames_posted = 0
    print("No progress.txt found. From the top...")

while True:
    # Get frame path and text to post
    (frame_filepath, post_text) = get_tweet_data(frame_dir, frames_posted)
    
    retries = 0
    success = False
    
    while not success and retries < 5:
        try:
            # Upload the image and create post on Bluesky
            with open(frame_filepath, 'rb') as f:
                img_data = f.read()
            
            # Send post with image
            response = client.send_image(
                text=post_text,
                image=img_data,
                image_alt=f"VEEP frame #{frames_posted + 1}"
            )
            
            print(f"Posted image {frame_filepath} to Bluesky")
            print(f"Post URI: {response.uri}")
            success = True
            
        except Exception as e:
            print(f'Error while posting image {frame_filepath}: {e}')
            retries += 1
            print('Trying again in 60 seconds.')
            time.sleep(60)
            
            # If we've had several failures, try to re-login
            if retries == 3:
                try:
                    client.login(BLUESKY_HANDLE, BLUESKY_PASSWORD)
                    print("Re-logged in to Bluesky")
                except Exception as login_error:
                    print(f"Error re-logging in: {login_error}")
    
    if not success:
        print(f'Failed to post image {frame_filepath} after {retries} attempts')
        # Wait for user input before exiting
        input("Too many errors. Press Enter to exit.")
        sys.exit()
    
    # Save progress to text file
    with open("progress.txt", "w") as f:
        frames_posted += 1
        f.write(str(frames_posted))
    
    print(f"Image posted. Waiting for {wait_time} seconds.\n")
    time.sleep(wait_time)
