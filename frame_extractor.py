# frame_extractor.py

import os
import cv2

def extract_frames(video_path, frame_numbers, output_folder):
    """
    Extracts specific frames from a video and saves them as images.

    Parameters:
        video_path (str): Path to the video file.
        frame_numbers (list): List of frame numbers to extract.
        output_folder (str): Directory to save the extracted frames.

    Returns:
        list: A list of file paths for the extracted frames.
    """
    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if the video opened successfully
    if not cap.isOpened():
        print("Error: Could not open video file.")
        return []

    # Ensure the output directory exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Frame counter
    frame_count = 0
    extracted_frames = []

    while True:
        # Read the next frame from the video
        ret, frame = cap.read()

        # If the frame could not be read, break the loop
        if not ret:
            break

        # Check if the current frame is in the list of frames to extract
        if frame_count in frame_numbers:
            frame_filename = os.path.join(output_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)  # Save the frame as a .jpg image
            extracted_frames.append(frame_filename)

        # Increment frame counter
        frame_count += 1

    # Release the video capture object
    cap.release()
    return extracted_frames
