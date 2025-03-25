import json
import pandas as pd
import os

# Generalized function to handle questions with two baselines
# Generalized function to handle questions with multiple items and case insensitivity
def calculate_win_rate_for_dds(questions, selections, baseline_1_name, baseline_2_name, propsed_name="dds"):
    # Convert model names to lowercase to handle case insensitivity
    baseline_1_name = baseline_1_name.lower()
    baseline_2_name = baseline_2_name.lower()
    propsed_name = propsed_name.lower()

    wins_baseline_1 = 0
    total_baseline_1 = 0
    wins_baseline_2 = 0
    total_baseline_2 = 0

    for i, q in enumerate(questions):
        # Extract the last two models for comparison
        model_3 = os.path.basename(q[-2].lower())  # Second last item in the list, convert to lowercase
        model_4 = os.path.basename(q[-1].lower())  # Last item in the list, convert to lowercase
        choice = selections[i]  # User selection

        # Check if dds is present in one of the two models
        if propsed_name in model_3:
            # If row 3 is dds, then row 4 is either baseline 1 or baseline 2
            if baseline_1_name in model_4:
                total_baseline_1 += 1
                if choice == 0:  # Chose dds (row 3)
                    wins_baseline_1 += 1
            elif baseline_2_name in model_4:
                total_baseline_2 += 1
                if choice == 0:  # Chose dds (row 3)
                    wins_baseline_2 += 1
        elif propsed_name in model_4:
            # If row 4 is dds, then row 3 is either baseline 1 or baseline 2
            if baseline_1_name in model_3:
                total_baseline_1 += 1
                if choice == 1:  # Chose dds (row 4)
                    wins_baseline_1 += 1
            elif baseline_2_name in model_3:
                total_baseline_2 += 1
                if choice == 1:  # Chose dds (row 4)
                    wins_baseline_2 += 1

    # Calculate win rates
    baseline_1_rate = wins_baseline_1 / total_baseline_1 if total_baseline_1 else 0
    baseline_2_rate = wins_baseline_2 / total_baseline_2 if total_baseline_2 else 0

    return baseline_1_rate, baseline_2_rate

def get_partial_answer(data, name='part1'):
    # Call the function to analyze the first question set
    processed_data = data[data['question_type'] == name].drop_duplicates()
    # Sort by 'value1' in ascending order
    processed_data = processed_data.sort_values(by=["question"])
    # Convert float to int
    processed_data["question"] = processed_data["question"].astype(int)
    processed_data["selection"] = processed_data["selection"].astype(int)
    return processed_data

with open('audio_questions1.json') as f:
    question_list1 = json.load(f)
with open('audio_questions2.json') as f:
    question_list2 = json.load(f)

data = pd.read_csv('user_ratings/d61480e7.csv')

# part 1
selections = get_partial_answer(data, 'test1')['selection'].values
part1_result = calculate_win_rate_for_dds(
    question_list1["audio_questions2"], selections, "musicmagus", "ZETA", 'dds'
)

# part 2
selections = get_partial_answer(data, 'test2')['selection'].values
part2_result = calculate_win_rate_for_dds(
    question_list2["audio_questions2"], selections, "textinv", "dreamsound", 'steermusic'
)

print(f"dds v.s. musicmagus: {part1_result[0]}\tdds v.s. ZETA: {part1_result[1]}")
print(f"steermusic v.s. textinv: {part2_result[0]}\tsteermusic v.s. dreamsound: {part2_result[1]}")