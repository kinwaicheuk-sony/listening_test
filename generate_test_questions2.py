import json
import re
from pathlib import Path

# Assign numbers to audio types
AUDIO_TYPE_MAP = {
    "steermusic": 0,
    "textinv": 1,
    "dreamsound": 2
}

# Control which audio types appear per sample
selection_control = [
    [0, 1], [2, 0], [1,0], [0, 2]
    ]  # Modify this to change the selection pattern

# Expected order
EXPECTED_ORDER = [
    "source.flac",
    "source_prompt.txt",
    "*_1.flac",
    "*_steermusic.flac",
    "*_textinv.flac",
    "*_dreamsound.flac"
]

def natural_sort_key(text):
    """ Extract numbers from text for proper numerical sorting (Sample1, Sample2, ..., Sample35) """
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', text)]

def get_ordered_files(sample_path, allowed_types):
    """ Get ordered files for a sample folder, filtering based on allowed_types """
    files = {pattern: [] for pattern in EXPECTED_ORDER}  # Dict to store categorized files
    selected_audio_files = []  # Store the selected two audio files

    # Sort and categorize files
    for file in sample_path.glob("*"):
        if file.suffix.lower() not in [".flac", ".txt"]:
            continue  # Ignore non-audio/non-text files

        filename_lower = file.name.lower()  # Convert to lowercase for matching
        for pattern in EXPECTED_ORDER:
            if pattern == filename_lower or (pattern.startswith("*") and filename_lower.endswith(pattern[1:])):
                files[pattern].append(file)

    # Flatten list while keeping order, but filtering .flac files properly
    ordered_files = []
    for pattern in EXPECTED_ORDER:
        if pattern in ["*_steermusic.flac", "*_textinv.flac", "*_dreamsound.flac"]:  
            audio_type = pattern.split("_")[-1].replace(".flac", "")  # Extract audio type (steermusic, textinv, dreamsound)
            if AUDIO_TYPE_MAP[audio_type] in allowed_types:
                selected_audio_files.append(files[pattern][0])  # Add the first match

        elif pattern in files:  
            ordered_files.extend(sorted(files[pattern]))  # Add all other files as normal

    # **Sort selected .flac files based on allowed_types order**
    selected_audio_files.sort(key=lambda x: allowed_types.index(AUDIO_TYPE_MAP[x.stem.split("_")[-1].lower()]))

    return [str(file.relative_to(sample_path.parent)) for file in ordered_files + selected_audio_files]  # Keep relative paths

def generate_audio_questions(root_dir, selection_control):
    """ Generate JSON with ordered audio file paths based on selection_control """
    data = {"audio_questions2": []}

    # Sort sample folders naturally (Sample1, Sample2, ..., Sample35)
    sample_folders = sorted(
        [f for f in root_dir.iterdir() if f.is_dir() and f.name.startswith("Sample")],
        key=lambda x: natural_sort_key(x.name)
    )

    for idx, sample_folder in enumerate(sample_folders):
        allowed_types = selection_control[idx % len(selection_control)]  # Cycle through selection control list
        ordered_files = get_ordered_files(sample_folder, allowed_types)
        if ordered_files:
            data["audio_questions2"].append(ordered_files)

    return data

# Set root directory where "SampleXX" folders are located
root_directory = Path("SteerMusic_demo_flac")  # Use relative path

# Generate the JSON data
audio_data = generate_audio_questions(root_directory, selection_control)

# Save to a JSON file
output_path = "audio_questions2.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(audio_data, f, indent=4)

print(f"JSON file saved as {output_path}")
