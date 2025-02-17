import os
import math
import whisper
from moviepy.editor import VideoFileClip

def split_video(video_path, clip_length, output_directory='Clips of video'):
    # Load the video file
    video = VideoFileClip(video_path)
    duration = video.duration  # Get the duration of the video in seconds
    
    # Ensure the output directory exists
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    # Calculate the number of clips to create
    num_clips = math.ceil(duration / clip_length)
    
    # Split the video into clips
    clips = []
    for i in range(num_clips):
        start_time = i * clip_length
        end_time = min((i + 1) * clip_length, duration)
        clip = video.subclip(start_time, end_time)
        clip_name = os.path.join(output_directory, f'clip_{i+1}.mp4')
        clip.write_videofile(clip_name, codec='libx264', audio_codec='aac')  # Ensure audio is included
        clips.append(clip_name)
        print(f'Created clip: {clip_name}')
    
    video.close()
    return clips


# Usage
video_path = 'Access Able.mp4'  # Path to your video file
clip_length = 10  # Length of each clip in seconds
output_directory = r"C:\Users\Sharan Kumar\OneDrive\Documents\GitHub\Video-to-pdf-Step-by-step-tutorial-\Clips of video"  # Output directory

# Step 1: Split the video
clips = split_video(video_path, clip_length, output_directory)
