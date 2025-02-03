import cv2
import os

# Function to extract frames every 3 seconds from a video
def extract_frames(video_path, output_folder, interval_seconds=3):
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)  # Frames per second
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Total frames in the video
    duration = total_frames / fps  # Total duration in seconds
    
    print(f"Processing: {video_path}")
    print(f"Video FPS: {fps}")
    print(f"Total Frames: {total_frames}")
    print(f"Video Duration: {duration} seconds")
    
    # Calculate the frame interval for the given interval_seconds
    frame_interval = int(fps * interval_seconds)
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    frame_count = 0
    saved_frame_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break  # Exit the loop if no more frames are available
        
        # Save frame every `frame_interval` frames
        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(output_folder, f"frame_{saved_frame_count:04d}.jpg")
            cv2.imwrite(frame_filename, frame)
            print(f"Saved {frame_filename}")
            saved_frame_count += 1
        
        frame_count += 1
    
    # Release the video capture object
    cap.release()
    print(f"Finished processing {video_path}\n")

# Function to process all videos in a folder
def process_videos_in_folder(input_folder, output_base_folder, interval_seconds=3):
    # Get a list of all video files in the input folder
    video_files = [f for f in os.listdir(input_folder) if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]
    
    if not video_files:
        print(f"No video files found in {input_folder}")
        return
    
    # Process each video file
    for video_file in video_files:
        video_path = os.path.join(input_folder, video_file)
        
        # Create a subfolder for each video's frames
        video_name = os.path.splitext(video_file)[0]
        output_folder = os.path.join(output_base_folder, video_name)
        # Extract frames from the video
        extract_frames(video_path, output_folder, interval_seconds)

# Example usage
input_folder = "./Data/Video"  # Folder containing video files
output_base_folder = "./Data/Frame"  # Base folder to save extracted frames
process_videos_in_folder(input_folder, output_base_folder, interval_seconds=3)
