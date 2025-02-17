import json
import os
import time
from pathlib import Path
import tempfile
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from google.generativeai import upload_file, get_file
import google.generativeai as genai

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

# Folder containing video clips
VIDEO_FOLDER = "Clips of video"
OUTPUT_JSON_FILE = "step_by_step_video.json"

# Initialize AI Agent
def initialize_agent():
    return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash"),  
        tools=[DuckDuckGo()],
        markdown=True,
    )

# Function to analyze a single video
def analyze_video(video_path, step_number):
    try:
        processed_video = upload_file(video_path)
        while processed_video.state.name == "PROCESSING":
            time.sleep(1)
            processed_video = get_file(processed_video.name)

        analysis_prompt = f"""
        This video is part of a step-by-step process. Ensure that it follows the correct sequence.
        Format the output as:
        
        Step {step_number}: <Summary of this video>

        Make sure to maintain logical continuity from the previous steps.
        """

        multimodal_agent = initialize_agent()
        response = multimodal_agent.run(analysis_prompt, videos=[processed_video])

        return response.content

    except Exception as error:
        print(f"❌ Error analyzing {video_path}: {error}")
        return None
    finally:
        Path(video_path).unlink(missing_ok=True)

# Function to process all videos in a folder and ensure continuity
def process_all_videos(folder_path):
    results = []
    video_files = sorted(
        [f for f in os.listdir(folder_path) if f.endswith(".mp4")],
        key=lambda x: int(''.join(filter(str.isdigit, x)))  
    )

    if not video_files:
        print("❌ No video files found in the folder.")
        return

    print(f"📂 Found {len(video_files)} video files. Processing...")

    step_number = 1  # Start from step 1

    for video_file in video_files:
        video_path = os.path.join(folder_path, video_file)

        print(f"🎬 Analyzing: {video_file}")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
            with open(video_path, "rb") as f:
                temp_video.write(f.read())
            temp_video_path = temp_video.name

        response = analyze_video(temp_video_path, step_number)

        if response:
            results.append(response)
            print(f"✅ Analysis complete for {video_file}")
            step_number += 1  # Increment step number
        else:
            print(f"⚠️ No response received for {video_file}")

    # Save results in step-by-step format
    structured_summary = {"steps": results}

    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as json_file:
        json.dump(structured_summary, json_file, indent=4, ensure_ascii=False)

    print(f"📄 Step-by-step summary saved to {OUTPUT_JSON_FILE}")

# Run processing for all videos
if __name__ == "__main__":
    process_all_videos(VIDEO_FOLDER)
