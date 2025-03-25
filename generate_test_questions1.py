import json
import re
import random
from pathlib import Path

# Assign numbers to audio types
AUDIO_TYPE_MAP = {
    "dds": 0,
    "ddim": 1,
    "musicmagus": 2,
    "sdedit": 3,
    "zeta": 4,
}

# Control which audio types appear per sample
selection_control = [[0, 2], [4, 0]]  # Modify this to change the selection pattern

# Expected order
EXPECTED_ORDER = [
    "source.flac",
    "prompt.txt",
    "dds.flac",
    "ddim.flac",
    "musicmagus.flac",
    "sdedit.flac",
    "zeta.flac",
]


def natural_sort_key(text):
    """ Extract numbers from text for proper numerical sorting (Sample1, Sample2, ..., Sample35) """
    return [int(t) if t.isdigit() else t for t in re.split(r'(\d+)', text)]


def get_ordered_files(sample_path, allowed_types):
    """ Get ordered files for a sample folder, filtering based on allowed_types """
    files = {pattern: [] for pattern in EXPECTED_ORDER}  # Dict to store categorized files
    selected_audio_files = []  # Store the selected two audio files
    numbered_flac_files = []  # Store any *_X.flac files (where X is a digit)

    # Sort and categorize files
    for file in sample_path.glob("*"):
        if file.suffix.lower() not in [".flac", ".txt"]:
            continue  # Ignore non-audio/non-text files

        filename_lower = file.name.lower()  # Convert to lowercase for matching

        # Match dynamically named numbered flac files (e.g., bouzouki_1.flac, violin_2.flac)
        if re.match(r".*_\d\.flac$", filename_lower):
            numbered_flac_files.append(file)
            continue  # Skip explicit checks in EXPECTED_ORDER

        for pattern in EXPECTED_ORDER:
            if pattern == filename_lower or (pattern.startswith("*") and filename_lower.endswith(pattern[1:])):
                files[pattern].append(file)

    # Flatten list while keeping order, but filtering .flac files properly
    ordered_files = []

    # First, add source files and prompt
    for pattern in EXPECTED_ORDER:
        if pattern in ["source.flac", "prompt.txt"]:
            ordered_files.extend(sorted(files[pattern]))  # Add as normal

    # Then, add *_X.flac files (sorted naturally)
    ordered_files.extend(sorted(numbered_flac_files, key=lambda x: natural_sort_key(x.name)))

    # Then, add the selected audio type files based on `allowed_types`
    for pattern in ["dds.flac", "ddim.flac", "musicmagus.flac", "sdedit.flac", "zeta.flac"]:
        audio_type = pattern.split("_")[-1].replace(".flac", "")  # Extract audio type
        if AUDIO_TYPE_MAP[audio_type] in allowed_types and files[pattern]:
            selected_audio_files.append(files[pattern][0])  # Add the first match

    # **Sort selected .flac files based on allowed_types order**
    selected_audio_files.sort(key=lambda x: allowed_types.index(AUDIO_TYPE_MAP[x.stem.split("_")[-1].lower()]))

    return [str(file.relative_to(sample_path.parent)) for file in ordered_files + selected_audio_files]  # Keep relative paths


def generate_audio_questions(root_dir, selection_control, exclude_samples, shuffle_order):
    """ Generate JSON with ordered audio file paths based on selection_control and apply shuffling """
    data = {"audio_questions2": []}

    # Sort sample folders naturally (Sample1, Sample2, ..., Sample35)
    sample_folders = sorted(
        [f for f in root_dir.iterdir() 
         if f.is_dir() and f.name.startswith("Sample") and f.name not in exclude_samples],
        key=lambda x: natural_sort_key(x.name)
    )

    for idx, sample_folder in enumerate(sample_folders):
        for selection in selection_control:  # Iterate over all selection patterns
            ordered_files = get_ordered_files(sample_folder, selection)
            if ordered_files:
                # Adjust paths to include the root directory
                data["audio_questions2"].append([str(root_dir / Path(file)) for file in ordered_files])

    # Apply shuffling based on shuffle_order
    if len(shuffle_order) == len(data["audio_questions2"]):
        data["audio_questions2"] = [data["audio_questions2"][i] for i in shuffle_order]
    else:
        print("Warning: Shuffle list does not match the number of questions. Skipping shuffle.")

    return data


# Set root directory where "SampleXX" folders are located
root_directory = Path("SteerEdit_demo_flac")  # Use relative path

# List of samples to exclude
exclude_samples = {
    "Sample2", "Sample3", "Sample14", "Sample9",
    "Sample4", "Sample7", "Sample10", "Sample13",
    "Sample15", "Sample12", "Sample11", "Sample10"
    "Sample17", "Sample20", "Sample21", "Sample24",
    "Sample25", "Sample26", "Sample28", "Sample29",
    "Sample31", "Sample32", "Sample33", "Sample33",
    "Sample34", "Sample35", "Sample36", "Sample37",
    "Sample38", "Sample39", "Sample30", "Sample22",
}

# Predefined shuffle order
shuffled_question_numbers = [12, 3, 7, 1, 9, 18, 4, 0, 15, 6, 2, 5, 19, 8, 14, 11, 17, 10, 16, 13]

# sample18 musicmagus is better
# Generate the JSON data with shuffling
audio_data = generate_audio_questions(root_directory, selection_control, exclude_samples, shuffled_question_numbers)

# Save to a JSON file
output_path = "audio_questions1.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(audio_data, f, indent=4)

print(f"JSON file saved as {output_path}")
