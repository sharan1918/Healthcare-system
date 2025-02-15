import json
import os
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
VIDEO_ANALYSIS_FILE = "video_analysis_results.json"
STRUCTURED_VIDEO_SUMMARY_FILE = "structured_video_summary.json"
OUTPUT_JSON_FILE = "combined_video_analysis.json"

# Load the existing JSON data
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# Combine the two JSON files
def combine_json_data():
    video_analysis = load_json(VIDEO_ANALYSIS_FILE)
    structured_summary = load_json(STRUCTURED_VIDEO_SUMMARY_FILE)
    
    combined_data = {
        "video_analysis": video_analysis["response"],
        "structured_summary": structured_summary["steps"]
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
def get_combined_steps_from_gemini():
    combined_data = combine_json_data()
    
    combined_prompt = f"""
    **Video Analysis Results:**
    {combined_data["video_analysis"]}

    **Structured Video Summary:**
    {json.dumps(combined_data["structured_summary"], indent=4, ensure_ascii=False)}

    Please merge these summaries, ensuring that:
    1. All steps are logically continuous, maintaining the context between each step.
    2. The summaries are precise and retain all key details.
    3. Make sure no steps are omitted, and each step includes relevant information from both summaries.
    
    Provide the combined, clear, and continuous step-by-step summary. 
    Avoid this videos says or shows, or similar phrases. Make it precise and clear. Just the steps to complete the task.
    Each step should be mapped to a corresponding clip (clip1, clip2, etc.). 
    Return the result as a dictionary, where each clip key (e.g., 'clip1', 'clip2') is associated with a step description.
    Include all the steps as in structured_summary file.
    """

    # Initialize the agent and send the prompt to Gemini
    multimodal_agent = initialize_agent()
    response = multimodal_agent.run(combined_prompt)

    return response.content

# Function to clean and structure the response
def clean_and_structure_response(response):
    structured_response = {}

    # Remove unwanted markers (e.g., ```json, }{, etc.)
    response = response.strip().replace("```json", "").replace("```", "").strip()

    # Split by lines or steps, assuming the response is separated by newlines
    steps = response.split("\n")
    
    # Filter out empty steps or invalid ones
    steps = [step.strip() for step in steps if step.strip() and step not in ['{', '}']]

    # Map each step to the corresponding clip (clip1, clip2, etc.)
    for index, step in enumerate(steps, start=1):
        clip_key = f"clip{index}"
        structured_response[clip_key] = step.strip()

    return structured_response

# Save the structured response to a file
def save_combined_response(structured_response):
    with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as json_file:
        json.dump(structured_response, json_file, indent=4, ensure_ascii=False)
    print(f"Combined video summary saved to {OUTPUT_JSON_FILE}")

# Main function to get combined steps and save the output
def process_and_save_combined_steps():
    response = get_combined_steps_from_gemini()

    if response:
        structured_response = clean_and_structure_response(response)
        save_combined_response(structured_response)
    else:
        print("❌ No response received from Gemini.")

# Run the process
if __name__ == "__main__":
    process_and_save_combined_steps()
