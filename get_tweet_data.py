import os
from showenv import show_name


def get_sorted_jpegs(folder_path):
    # Initialize an empty list to hold all JPEG file paths
    jpeg_files = []

    # Walk through the directory tree starting at folder_path
    for root, _, files in os.walk(folder_path):
        for file in files:
            # Check if the file is a JPEG (case-insensitive)
            if file.lower().endswith((".jpeg", ".jpg")):
                # Add the full path of the JPEG file to the list
                jpeg_files.append(os.path.join(root, file))

    # Sort the list of JPEG file paths alphabetically
    jpeg_files.sort()

    return jpeg_files


def extract_jpeg_info(jpeg_filepath):
    # Extract the directory and filename
    frames_folder, filename = os.path.split(jpeg_filepath)
    print(frames_folder)
    directory = os.path.dirname(frames_folder)



    # Extract the season and episode folder
    _, episode_folder = os.path.split(directory)
    

    # Parse the season number, episode number, and title from the folder name
    try:
        season_and_episode, episode_title = episode_folder.split(" - ")
        season_part, episode_number = season_and_episode.split("E")
        
        title = episode_title.strip()
        season_number = int(season_part[1:].strip())
        episode_number = int(episode_number.strip())
    except ValueError:
        print(
            "Error parsing the folder structure. Please ensure the format is correct."
        )
        return None

    # List all files in the episode folder and filter JPEGs
    jpeg_files = [
        f
        for f in os.listdir(frames_folder)
        if f.lower().endswith(".jpeg") or f.lower().endswith(".jpg")
    ]

    # Sort JPEG files alphabetically
    jpeg_files.sort()

    # Find the current frame position and total frames
    current_frame_index = jpeg_files.index(filename)
    nth_frame = current_frame_index + 1  # Convert to 1-based index
    total_frames = len(jpeg_files)

    # Return the extracted information
    return {
        "season_number": season_number,
        "episode_number": episode_number,
        "title": title,
        "nth_frame": nth_frame,
        "total_frames": total_frames,
    }


def get_tweet_data(folder_path, skips):
    jpeg_filepath = get_sorted_jpegs(folder_path)[skips]
    t = extract_jpeg_info(jpeg_filepath)

    tweet_text = (
        f'{show_name} S{t["season_number"]}E{t["episode_number"]}'
        + f' - {t["title"]} \nFrame {t["nth_frame"]} of {t["total_frames"]}'
    )
    return(jpeg_filepath, tweet_text)
