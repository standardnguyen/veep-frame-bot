# video_processor.py

from frame_metrics import extract_frame_metrics
from key_frame_identifier import identify_key_frames
from frame_extractor import extract_frames

def process_and_extract_key_frames(
    video_path,
    output_folder,
    ssim_threshold=0.95,
    ssim_threshold_top=0.95,
    ssim_threshold_bottom=0.95,
    histogram_similarity_threshold=0.7,
    time_threshold=1.26,
    fps=30
):
    """
    Processes a video to identify and extract key frames based on specified criteria.

    Parameters:
        video_path (str): Path to the video file.
        output_folder (str): Directory to save the extracted frames.
        ssim_threshold (float): SSIM threshold for the whole frame. Default is 0.95.
        ssim_threshold_top (float): SSIM threshold for the top third of the frame. Default is 0.95.
        ssim_threshold_bottom (float): SSIM threshold for the bottom third of the frame. Default is 0.95.
        histogram_similarity_threshold (float): Histogram similarity threshold. Default is 0.7.
        time_threshold (float): Time threshold in seconds. Default is 1.
        fps (int): Frames per second of the video. Default is 30.

    Returns:
        list: A list of file paths for the extracted key frames.
    """
    print(f"Working on video: {video_path}")
    # Extract frame metrics
    frame_dict = extract_frame_metrics(video_path)

    # Identify key frames
    key_frame_ids = identify_key_frames(
        frame_dict,
        ssim_threshold,
        ssim_threshold_top,
        ssim_threshold_bottom,
        histogram_similarity_threshold,
        time_threshold,
        fps
    )

    # Extract the identified key frames
    extracted_frames = extract_frames(video_path, key_frame_ids, output_folder)

    # Return the extracted frame file paths
    return extracted_frames

if __name__ == "__main__":
    video_path = "test.mkv"  # Path to the video file
    output_folder = "output_frames"  # Directory to save extracted frames

    # Call the process function with default thresholds
    extracted_frames = process_and_extract_key_frames(
        video_path,
        output_folder
    )

    # Print the extracted frame file paths
    print("Extracted frames:", extracted_frames)
