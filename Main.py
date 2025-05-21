import os
import tempfile
from Full_video_analysis import analyze_video
from Step_by_step_response import process_all_videos
from two_api import process_and_save_combined_steps
from Capture_screenshots import capture_screenshots
from Pdf_maker import create_word_document
from dotenv import load_dotenv
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo
from time import perf_counter

# ✅ Load environment variables
load_dotenv()
# ✅ Set API Key Once
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")

# ✅ Initialize the AI Model Once
gemini_model = Agent(
    name="Video AI Summarizer",
    model=Gemini(id="gemini-2.0-flash"),
    tools=[DuckDuckGo()],
    markdown=True,
)

# ✅ User Query (Set Once)
user_query = "Summarize the video in detail"

# ✅ Define Paths
video_path = "Access Able.mp4"  # Path to the input video
clip_length = 10  # Length of each clip in seconds
output_directory = "Clips of video"
screenshots_folder = "Screenshots"
video_summary_file = "Final_combined.json"
output_document = "Video_Summary.docx"

# ✅ Measure the time taken for the entire process
start_time = perf_counter()
# ✅ Step 1: Split the Video into Clips
if not os.path.exists(video_path):
    print("❌ Error: Video file not found.")
    exit()
else:
    print("📌 Splitting video into clips...")
    #clips = split_video(video_path, clip_length, output_directory)

# ✅ Step 2: Analyze the Full Video
with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
    with open(video_path, "rb") as f:
        temp_video.write(f.read())
    video_path_temp = temp_video.name

print("📌 Analyzing full video...")
analysis_results = analyze_video(video_path_temp, user_query, gemini_model)

if analysis_results:
    print("✅ Full video analysis complete!")

# ✅ Step 3: Process Each Clip for Step-by-Step Response
print("📌 Processing clips for step-by-step responses...")
process_all_videos(output_directory, gemini_model)

# ✅ Step 4: Combine Full Video and Step-by-Step Summaries
print("📌 Merging full and structured summaries...")
process_and_save_combined_steps(gemini_model)

# ✅ Step 5: Capture Screenshots from Clips
print("📌 Capturing screenshots from clips...")
capture_screenshots(output_directory, screenshots_folder)

# ✅ Step 6: Generate the PDF/Word Document
print("📌 Generating final document with summaries and screenshots...")
create_word_document(video_summary_file, screenshots_folder, output_document)

print("🎉 Process Complete! Summary saved in:", output_document)

print(f"Timetaken to complete the process: {perf_counter() - start_time:.2f} seconds")
