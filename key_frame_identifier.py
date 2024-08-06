# key_frame_identifier.py

def identify_key_frames(frame_dict, ssim_threshold, ssim_threshold_top, ssim_threshold_bottom, histogram_similarity_threshold, time_threshold, fps=30):
    """
    Identifies key frames from the given frame metrics based on specified thresholds.

    Parameters:
        frame_dict (dict): A dictionary containing metrics for each frame.
        ssim_threshold (float): SSIM threshold for the whole frame.
        ssim_threshold_top (float): SSIM threshold for the top third of the frame.
        ssim_threshold_bottom (float): SSIM threshold for the bottom third of the frame.
        histogram_similarity_threshold (float): Histogram similarity threshold.
        time_threshold (float): Time threshold in seconds.
        fps (int): Frames per second of the video.

    Returns:
        list: A list of frame IDs identified as key frames.
    """
    key_frame_ids = []
    time_counter = 0

    for frame_id, metrics in frame_dict.items():
        # if frame_id < 400:
        #     continue

        # Increment time counter based on frame rate
        time_counter += 1 / fps

        # Calculate difference scores for conditions
        condition_1 = ssim_threshold - metrics["ssim_overall"]
        condition_2 = ssim_threshold_top - metrics["ssim_top"]
        condition_3 = ssim_threshold_bottom - metrics["ssim_bottom"]
        condition_4 = histogram_similarity_threshold - metrics["histogram_similarity"]
        condition_5 = time_counter - time_threshold

        # Determine if current frame is a key frame
        if condition_1 + condition_2 + condition_3 + condition_4 + condition_5 > 1:
            key_frame_ids.append(frame_id)
            time_counter = 0  # Reset time counter after identifying a key frame

    return key_frame_ids
