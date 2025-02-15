# import cv2
# import os

# def capture_screenshots(video_folder, output_folder):
#     # List all video files in the specified folder
#     video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))]
    
#     for video_file in video_files:
#         path = os.path.join(video_folder, video_file)
#         cap = cv2.VideoCapture(path)
        
#         if not cap.isOpened():
#             print(f"Failed to open video {video_file}")
#             continue
        
#         frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
#         # Define frame indexes: 25% and 75% of the video
#         frames_to_capture = [int(frame_count * 0.25), int(frame_count * 0.75)]
        
#         for idx in frames_to_capture:
#             # Set the frame position
#             cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
#             ret, frame = cap.read()
#             if ret:
#                 # Define the part of the video (25% or 75%)
#                 part = '25%' if idx == int(frame_count * 0.25) else '75%'
#                 # Save the frame as an image file
#                 output_filename = f"{os.path.splitext(video_file)[0]}_{part}.jpg"
#                 output_path = os.path.join(output_folder, output_filename)
#                 cv2.imwrite(output_path, frame)
#                 print(f"Saved {output_path}")
#             else:
#                 print(f"Failed to capture frame at index {idx} for video {video_file}")
        
#         cap.release()


# # Specify the path to your video clips and the output directory for screenshots
# video_folder = "Clips of video"
# output_folder = "Screenshots"

# # Create the output folder if it does not exist
# if not os.path.exists(output_folder):
#     os.makedirs(output_folder)

# capture_screenshots(video_folder, output_folder)
import cv2
import os

def capture_screenshots(video_folder, output_folder):
    video_files = [f for f in os.listdir(video_folder) if f.endswith(('.mp4', '.avi'))]
    
    for video_file in video_files:
        path = os.path.join(video_folder, video_file)
        cap = cv2.VideoCapture(path)
        
        if not cap.isOpened():
            print(f"Failed to open video {video_file}")
            continue
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        # Define frame indexes for 25% and 75% of the video length
        if frame_count < 4:  # Check if the video is too short
            print(f"Video {video_file} is too short for meaningful frame capture.")
            continue
        
        frames_to_capture = [int(frame_count * 0.20), int(frame_count * 0.65)]
        
        for idx in frames_to_capture:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if ret:
                part = '20%' if idx == int(frame_count * 0.20) else '65%'
                output_filename = f"{os.path.splitext(video_file)[0]}_{part}.jpg"
                output_path = os.path.join(output_folder, output_filename)
                cv2.imwrite(output_path, frame)
                print(f"Saved {output_path}")
            else:
                print(f"Failed to capture frame at index {idx} for video {video_file}")
        
        cap.release()

# Specify the path to your video clips and the output directory for screenshots
video_folder = "Clips of video"
output_folder = "Screenshots"

# Create the output folder if it does not exist
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

capture_screenshots(video_folder, output_folder)
