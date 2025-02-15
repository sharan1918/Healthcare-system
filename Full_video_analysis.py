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

load_dotenv()

API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")


def initialize_agent():
    return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),  # Or a suitable Gemini model
        tools=[DuckDuckGo()],
        markdown=True,
    )

def analyze_video(video_path, user_query):
    try:
        # Upload and process video file
        processed_video = upload_file(video_path)
        while processed_video.state.name == "PROCESSING":
            time.sleep(1)
            processed_video = get_file(processed_video.name)

        # Prompt generation for analysis
        analysis_prompt = (
            f"""
            Analyze the uploaded video for content and context.
            Respond to the following query using video insights and supplementary web research:
            {user_query}

            Provide a detailed, user-friendly, and actionable response.
            """
        )

        # AI agent processing
        multimodal_agent = initialize_agent() # Initialize agent here to avoid caching issues in non-streamlit env
        response = multimodal_agent.run(analysis_prompt, videos=[processed_video])

        # Store results in JSON format
        results = {
            "query": user_query,
            "response": response.content
        }

        with open("video_analysis_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)

        print("Analysis complete. Results saved to video_analysis_results.json")
        return results

    except Exception as error:
        print(f"An error occurred during analysis: {error}")
        return None
    finally:
        # Clean up temporary video file
        Path(video_path).unlink(missing_ok=True)


if __name__ == "__main__":
    video_file_path = r"D:\Telic projects\How to do maker\Access Able.mp4" # Get video path from user
    if not os.path.exists(video_file_path):
        print("Error: Video file not found.")
        exit()

    user_question = "Summarize the video step by step"

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video:
        with open(video_file_path, "rb") as f:
            temp_video.write(f.read())
        video_path_temp = temp_video.name
        
    analysis_results = analyze_video(video_path_temp, user_question)

    if analysis_results:
        print("Analysis Results:\n", analysis_results['response'])