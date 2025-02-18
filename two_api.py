import json
import os
import re
from dotenv import load_dotenv
import google.generativeai as genai
from phi.agent import Agent
from phi.model.google import Gemini
from phi.tools.duckduckgo import DuckDuckGo

# Load API key
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    raise ValueError("GOOGLE_API_KEY environment variable not set.")

# Paths for JSON files
VIDEO_ANALYSIS_FILE = "full_video.json"
STRUCTURED_VIDEO_SUMMARY_FILE = "step_by_step_video.json"
OUTPUT_JSON_FILE = "Final_combined.json"

# Load the existing JSON data
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Combine the two JSON files
def combine_json_data():
    video_analysis = load_json(VIDEO_ANALYSIS_FILE)
    structured_summary = load_json(STRUCTURED_VIDEO_SUMMARY_FILE)
    
    combined_data = {
        "video_analysis": video_analysis.get("response", ""),
        "structured_summary": structured_summary.get("steps", [])
    }
    return combined_data

# Initialize AI Agent
def initialize_agent():
    return Agent(
        name="Video AI Summarizer",
        model=Gemini(id="gemini-2.0-flash-exp"),  
        tools=[DuckDuckGo()],
        markdown=True,
    )

# Function to get a combined step-by-step summary from Gemini
def get_combined_steps_from_gemini(gemini_model):
    combined_data = combine_json_data()
    
    combined_prompt = f"""
    **Video Analysis Results:**
    {combined_data["video_analysis"]}

    **Structured Video Summary:**
    {json.dumps(combined_data["structured_summary"], indent=4, ensure_ascii=False)}

    Please merge these summaries, ensuring that:
    1. All steps are logically continuous, maintaining the context between each step.
    2. The summaries are precise and retain all key details.
    3. For data accuracy, check with the video analysis results for each structured video step.
    
    Provide the combined, clear, and continuous step-by-step summary in a structured JSON format.
    All the clips should be included as in structured video summary.
    Give straightforward and actionable steps for the user to follow.
    Avoid "this video explains how to..." or "the video shows how to..., the video demonstrates, like this" in the summary.
    Each step should be mapped to a corresponding clip (clip1, clip2, etc.).
    Ensure the output is in the following format:
    
    {{
        "clip1": "Step description 1",
        "clip2": "Step description 2",
        ...
    }}
    """

    # Initialize the agent and send the prompt to Gemini
    response = gemini_model.run(combined_prompt)

    return response.content if response else None

# Function to clean and structure the response
def clean_and_structure_response(response):
    structured_response = {}
    
    # Remove unnecessary formatting markers (e.g., ```json, ``` etc.)
    response = response.strip().replace("```json", "").replace("```", "").strip()

    # Extract step-based content using regex
    step_pattern = re.compile(r"(clip\d+):\s*(.+)", re.IGNORECASE)
    matches = step_pattern.findall(response)

    for clip, description in matches:
        structured_response[clip.lower()] = description.strip()

    # If regex extraction fails, try JSON parsing
    if not structured_response:
        try:
            structured_response = json.loads(response)
        except json.JSONDecodeError:
            print("⚠️ Failed to parse response as JSON. Storing raw response.")

    return structured_response

# Save the structured response to a file
def save_combined_response(structured_response):
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as json_file:
        json.dump(structured_response, json_file, indent=4, ensure_ascii=False)
    print(f"✅ Combined video summary saved to {OUTPUT_JSON_FILE}")

# Main function to get combined steps and save the output
def process_and_save_combined_steps(gemini_model):
    response = get_combined_steps_from_gemini(gemini_model)

    if response:
        structured_response = clean_and_structure_response(response)
        save_combined_response(structured_response)
    else:
        print("❌ No response received from Gemini.")

# Run the process
if __name__ == "__main__":
    process_and_save_combined_steps()
