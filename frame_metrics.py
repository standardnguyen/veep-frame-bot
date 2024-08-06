# frame_metrics.py

import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from compute_histogram_similarity import compute_histogram_similarity

def extract_frame_metrics(video_path):
    """
    Extracts metrics for each frame in the video, including SSIM and histogram similarity.

    Parameters:
        video_path (str): Path to the video file.

    Returns:
        dict: A dictionary with frame indices as keys and metrics as values.
    """
    cap = cv2.VideoCapture(video_path)
    prev_frame_gray = None
    prev_frame_color = None
    frame_count = 0
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_metrics = {}

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the current frame to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if prev_frame_gray is not None and prev_frame_color is not None:
            # Compute SSIM for the whole frame
            ssim_overall = ssim(prev_frame_gray, gray_frame)

            # Compute SSIM for the top third
            ssim_top = ssim(
                prev_frame_gray[:gray_frame.shape[0]//3],
                gray_frame[:gray_frame.shape[0]//3]
            )

            # Compute SSIM for the bottom third
            ssim_bottom = ssim(
                prev_frame_gray[2*gray_frame.shape[0]//3:],
                gray_frame[2*gray_frame.shape[0]//3:]
            )

            # Compute histogram similarity
            histogram_similarity = compute_histogram_similarity(prev_frame_color, frame)

            # Store metrics for the current frame
            frame_metrics[frame_count] = {
                "ssim_overall": ssim_overall,
                "ssim_top": ssim_top,
                "ssim_bottom": ssim_bottom,
                "histogram_similarity": histogram_similarity
            }

        # Update the previous frames
        prev_frame_gray = gray_frame
        prev_frame_color = frame
        frame_count += 1

    cap.release()
    return frame_metrics
