import json
import os
from docx import Document
from docx.shared import Inches

def load_json_data(filepath):
    """Utility function to load JSON data from a file."""
    with open(filepath, 'r') as file:
        return json.load(file)

def find_screenshots_for_clip(clip_number, screenshots_folder):
    """Find all screenshots for a given clip number in the specified folder."""
    prefix = f"clip_{clip_number}_"
    return [f for f in os.listdir(screenshots_folder) if f.startswith(prefix)]

def create_word_document(video_summary_file, screenshots_folder, output_file):
    # Load data from the JSON file
    summaries = load_json_data(video_summary_file)

    # Create a new Word document
    doc = Document()
    doc.add_heading('Video Clip Summaries and Screenshots', level=1)

    # Iterate through each video clip description
    for clip_id, description in summaries.items():
        # Add a heading for each clip
        doc.add_heading(f"Clip {clip_id.split('clip')[1]}", level=2)
        doc.add_paragraph(description)

        # Get clip number and find all screenshots for this clip
        clip_number = clip_id.split('clip')[1]
        screenshot_filenames = find_screenshots_for_clip(clip_number, screenshots_folder)
        
        # Add screenshots if available
        for filename in screenshot_filenames:
            path = os.path.join(screenshots_folder, filename)
            if os.path.exists(path):
                try:
                    doc.add_picture(path, width=Inches(4.0))
                except Exception as e:
                    print(f"Error adding picture {path}: {e}")
            else:
                print(f"Screenshot not found for {path}")

    # Save the document
    doc.save(output_file)

# Define the paths to your JSON file and the output document
video_summary_file = "Final_combined.json"
screenshots_folder = "Screenshots"
output_file = "Video_Summary.docx"

# Call the function to create the Word document
create_word_document(video_summary_file, screenshots_folder, output_file)
