import cv2
import cupy as cp
import torch
import torch.nn.functional as F
import numpy as np
import csv
import os

# Initialize device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

def compute_histogram_similarity_batch(frames1, frames2):
    """Compute histogram similarity for batches of frames using the correlation method on GPU."""
    similarities = []
    for frame1, frame2 in zip(frames1, frames2):
        # Convert frames to CuPy arrays for GPU computation
        frame1_cp = cp.array(frame1)
        frame2_cp = cp.array(frame2)

        # Compute histograms for each color channel using CuPy
        hist1 = cp.histogramdd(frame1_cp.reshape(-1, 3), bins=(8, 8, 8), range=[(0, 256), (0, 256), (0, 256)])[0]
        hist2 = cp.histogramdd(frame2_cp.reshape(-1, 3), bins=(8, 8, 8), range=[(0, 256), (0, 256), (0, 256)])[0]

        # Normalize histograms
        hist1 /= cp.linalg.norm(hist1)
        hist2 /= cp.linalg.norm(hist2)

        # Compute histogram correlation
        similarity = cp.correlate(hist1.ravel(), hist2.ravel())[0]
        similarities.append(similarity)

    return similarities

def compute_ssim_batch(frames1, frames2):
    """Compute SSIM for batches of grayscale images using PyTorch on GPU."""
    batch_ssim_values = []
    for img1, img2 in zip(frames1, frames2):
        img1 = torch.from_numpy(img1).float().to(device).unsqueeze(0).unsqueeze(0)
        img2 = torch.from_numpy(img2).float().to(device).unsqueeze(0).unsqueeze(0)

        # Calculate SSIM using PyTorch operations
        C1 = (0.01 * 255) ** 2
        C2 = (0.03 * 255) ** 2

        mu1 = F.avg_pool2d(img1, 3, 1, 1)
        mu2 = F.avg_pool2d(img2, 3, 1, 1)

        mu1_sq = mu1 ** 2
        mu2_sq = mu2 ** 2
        mu1_mu2 = mu1 * mu2

        sigma1_sq = F.avg_pool2d(img1 * img1, 3, 1, 1) - mu1_sq
        sigma2_sq = F.avg_pool2d(img2 * img2, 3, 1, 1) - mu2_sq
        sigma12 = F.avg_pool2d(img1 * img2, 3, 1, 1) - mu1_mu2

        ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))
        ssim_val = ssim_map.mean()

        batch_ssim_values.append(ssim_val.item())
        
    return batch_ssim_values

def check_ssim_for_caption_batch(frames1, frames2):
    """Check the SSIM for specific regions of a batch of frames."""
    ssim_top_batch = []
    ssim_bottom_batch = []

    for prev_frame, current_frame in zip(frames1, frames2):
        # Convert frames to grayscale
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        current_gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        # Get dimensions of the frame
        height, width = prev_gray.shape

        # Calculate the third heights and middle third width
        third_height = height // 3
        middle_third_width = width // 3

        # Define regions of interest (ROI)
        top_third_middle = (slice(0, third_height), slice(middle_third_width, middle_third_width * 2))
        bottom_third_middle = (slice(2 * third_height, height), slice(middle_third_width, middle_third_width * 2))

        # SSIM calculations for top and bottom regions using batch processing
        ssim_top = compute_ssim_batch(
            [prev_gray[top_third_middle]],
            [current_gray[top_third_middle]]
        )[0]

        ssim_bottom = compute_ssim_batch(
            [prev_gray[bottom_third_middle]],
            [current_gray[bottom_third_middle]]
        )[0]

        ssim_top_batch.append(ssim_top)
        ssim_bottom_batch.append(ssim_bottom)

    return ssim_top_batch, ssim_bottom_batch

def extract_key_frames_to_csv(video_path='test.mkv', csv_path='frame_analysis.csv', batch_size=1000):
    """Extract key frames from a video and save results to a CSV file."""
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    # Open CSV file for writing
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['frame_count', 'ssim_top', 'ssim_bottom', 'ssim_overall', 'histogram_similarity'])

        # Process frames in batches
        while cap.isOpened():
            frames = []
            for _ in range(batch_size):
                ret, frame = cap.read()
                if not ret:
                    break
                frames.append(frame)
            print("frames compiled. preparing frames.")

            if len(frames) < 2:
                break

            # Prepare frame pairs for batch processing
            frame_pairs = list(zip(frames[:-1], frames[1:]))
            print("frames prepared. computing similarities.")
            
            # Compute SSIMs for batches
            ssim_overall_batch = compute_ssim_batch(
                [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in frames[:-1]],
                [cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) for frame in frames[1:]]
            )

            # Compute SSIM for caption regions
            ssim_top_batch, ssim_bottom_batch = check_ssim_for_caption_batch(frames[:-1], frames[1:])

            # Compute histogram similarity for batches
            hist_sim_batch = compute_histogram_similarity_batch(frames[:-1], frames[1:])

            # Write results for the batch
            for j, (ssim_top, ssim_bottom, ssim_overall, hist_sim) in enumerate(
                zip(ssim_top_batch, ssim_bottom_batch, ssim_overall_batch, hist_sim_batch)
            ):
                writer.writerow([frame_count + j, ssim_top, ssim_bottom, ssim_overall, hist_sim])

            frame_count += len(frames) - 1
            print("processed batch. moving onto next batch.")

    cap.release()
    print(f"Processed {frame_count} frames in batches and saved results to {csv_path}")

if __name__ == "__main__":
    # Run the extraction with default parameters
    extract_key_frames_to_csv()
