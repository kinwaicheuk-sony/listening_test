import json
import re
from collections import Counter

# Define the priority order of file types
AUDIO_TYPE_MAP = {
    "dds": 0,
    "ddim": 1,
    "musicmagus": 2,
    "sdedit": 3,
    "zeta": 4,
}

def extract_label(sample_files, occurrence_counter):
    """ Determine the ground truth label and update counts for occurrences. """
    # Get only the dds|musicmagus|zeta
    selected_files = [f for f in sample_files if re.search(r"(dds|musicmagus|zeta)\.flac$", f, re.IGNORECASE)]

    
    if len(selected_files) != 2:
        return None  # Ensure exactly two files

    # Sort files by order in the sample list
    sorted_files = sorted(selected_files, key=lambda x: sample_files.index(x))

    # Extract labels
    match1 = re.search(r"(dds|musicmagus|zeta)\.flac$", sorted_files[0], re.IGNORECASE)
    match2 = re.search(r"(dds|musicmagus|zeta)\.flac$", sorted_files[1], re.IGNORECASE)

    if match1 and match2:
        label1 = match1.group(1).lower()
        label2 = match2.group(1).lower()

        # Update the occurrence count **only once per file**
        occurrence_counter[label1] += 1
        occurrence_counter[label2] += 1

        return 0 if AUDIO_TYPE_MAP[label1] < AUDIO_TYPE_MAP[label2] else 1

    return None

def generate_ground_truth(json_file):
    """ Load JSON and compute ground truth labels and occurrences. """
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    audio_questions = data["audio_questions2"]
    occurrence_counter = Counter()
    
    # Compute ground truth labels and count occurrences
    ground_truth_labels = []
    for sample in audio_questions:
        label = extract_label(sample, occurrence_counter)
        if label is not None:
            ground_truth_labels.append(label)

    # Prepare output dictionary
    output_data = {
        "ground_truth_labels": ground_truth_labels,
        "occurrences": dict(occurrence_counter)  # Convert Counter to dict for JSON output
    }

    return output_data

# Example usage
json_file = "audio_questions1.json"  # Replace with actual JSON file
output_data = generate_ground_truth(json_file)

# Save to a new JSON file
output_file = "ground_truth_with_occurrences_fixed1.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(output_data, f, indent=4)

print("Ground truth labels:", output_data["ground_truth_labels"])
print("Occurrences:", output_data["occurrences"])
print(f"Saved to {output_file}")
