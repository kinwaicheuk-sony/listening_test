import streamlit as st
import pandas as pd
import os
import uuid
import datetime
import json
import re

# Directory to store user ratings
ratings_dir = "user_ratings"
os.makedirs(ratings_dir, exist_ok=True)

# Load JSON file
with open("audio_questions.json", "r") as f:
    audio_config = json.load(f)

tutorial_questions = audio_config["tutorial_questions"]
audio_questions = audio_config["audio_questions"]
audio_questions2 = audio_config["audio_questions2"]


# parse target concept from the txt file
def get_label_from_folder(folder_path):
    for file in os.listdir(folder_path):
        if file.endswith(".txt") and "prompt" not in file.lower():
            return os.path.splitext(file)[0]  # Get filename without extension
    return None  # Return None if no .txt file is found

# refresh page when clicking on the navigation pane
def update_page():
    st.session_state.page = st.session_state.page_selection

# Rating buttons
def render_rating_buttons(num_buttons, label, instruction, model_index, q_index, log, key_prefix):
    """Generalized function to render rating buttons."""
    st.write(f"##### {label}")
    mos_score = {0: "Bad", 1: "Poor", 2: "Fair", 3: "Good", 4: "Excellent"}

    if 'tutorial' in key_prefix:
        # Retrieve previous selection if it exists
        previous_selections = log.get(q_index, None)
        previous_selection = previous_selections[model_index] if previous_selections is not None else None
    elif 'test' in key_prefix:
        # Retrieve previous selection if it exists
        previous_selections = log.get(q_index, None)
        previous_selection = previous_selections[model_index] if previous_selections is not None else None

    # Render radio buttons
    selected_option = st.radio(
        f" {instruction}",
        options=list(range(num_buttons)),
        format_func=lambda x: f"{x + 1}: {mos_score[x]}",
        index=previous_selection if previous_selection is not None else None,
        key=f"{key_prefix}_{model_index}_{q_index}"
    )

    return selected_option



# ========== Parameters Initalization ============
# Dictionarys for answers storing
# activate only once
# t2: tutorial 2, p1: test 1
if "ratings" not in st.session_state:
    st.session_state.ratings = {key: {} for key in ["t1_q1", "t1_q2", "t2_q1", "t2_q2", "p1_q1", "p1_q2", "p2_q1", "p2_q2"]}

# store question types: flow of the study tutorial -> test
if "question_type" not in st.session_state:
    st.session_state.question_type = "tutorial"  # Default to tutorial

if "user_info_collected" not in st.session_state:
    st.session_state.user_info_collected = False
    st.session_state.listener_id = str(uuid.uuid4())[:8]  # Auto-generate listener ID
    st.session_state.age = None
    st.session_state.music_training_years = None
    # st.session_state.question_index = 0  # Track current question
    st.session_state.tutorial_index = 0  # Track tutorial question index separately
    st.session_state.test_index = 0  # Track test question index separately
    st.session_state.test_index2 = 0  # Track test question index separately 
    st.session_state.test_completed = False
    st.session_state.test_completed2 = False
    st.session_state.start_time = datetime.datetime.now()
    st.session_state.selected_ratings = None
    st.session_state.selected_ratings2 = None

    if "page" not in st.session_state:
        st.session_state.page = "User Info"  # Start with user info page

# ========== End of Parameters Initalization ============

# ========== Start of UI ============
# Title
st.title("Audio Rating App")

# Sidebar Navigation
st.sidebar.title("Navigation")
page_options = ["User Info", "Tutorial 1", "Listening test 1", "Tutorial 2", "Listening test 2"]
st.session_state.page = st.sidebar.radio("Current progress", page_options, index=page_options.index(st.session_state.page), key="page_selection", on_change=update_page)

# User Info Page
if st.session_state.page == "User Info":
    st.write("### Information for users")
    st.write("This project evaluates generative AI techniques for music style editing.")
    st.text(f"Your Listener ID: {st.session_state.listener_id}")
    st.session_state.age = st.number_input("Enter your age", min_value=18, max_value=100, step=1)
    st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)), index=st.session_state.music_training_years or 0)
    
    if st.button("Submit & Start Test"):
        if None in [st.session_state.age, st.session_state.music_training_years]:
            st.error("Please fill in all required fields before proceeding.")
        else:
            user_ratings_file = os.path.join(ratings_dir, f"{st.session_state.listener_id}.csv")
            pd.DataFrame([{ "listener_id": st.session_state.listener_id, "age": st.session_state.age, "music_training_years": st.session_state.music_training_years, "start_time": st.session_state.start_time }]).to_csv(user_ratings_file, index=False)
            st.session_state.user_ratings_file = user_ratings_file
            st.session_state.user_info_collected = True
            st.session_state.page = "Tutorial 1"
            st.success("Information saved! Proceed to the test.")
            st.rerun()

elif "Tutorial" in st.session_state.page: 
    tutorial_index = 0 if st.session_state.page == "Tutorial 1" else 1
    dict_name1 = f"t{tutorial_index + 1}_q1"
    dict_name2 = f"t{tutorial_index + 1}_q2"     
    file_paths = tutorial_questions[tutorial_index]
    st.write(f"#### Tutorial {tutorial_index + 1}")
    st.text(f"Listener ID: {st.session_state.listener_id}")

    st.write("#### Source Audio")
    st.audio(file_paths[0], format="audio/flac")
    st.write("#### Edited Result")
    st.audio(file_paths[1], format="audio/flac")

    answer_list_1, answer_list_2 = [], []

    answer_list_1.append(render_rating_buttons(
        5, "Example 1", "Rate content consistency with source music", 0,
        tutorial_index, st.session_state.ratings[dict_name1],
        f"tutorial{tutorial_index + 1}q1"))
    answer_list_2.append(render_rating_buttons(
        5, "Example 2", "Rate style match", 0,
        tutorial_index, st.session_state.ratings[dict_name2],
        f"tutorial{tutorial_index + 1}q2"))
    
    if st.button("Next"):
        if (None in answer_list_1) or (None in answer_list_2):
            st.error("Please select your rating before proceeding.")
        else:
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)
            if st.session_state.tutorial_index not in st.session_state.ratings[dict_name1]: 
                user_ratings_df = pd.concat(
                    [user_ratings_df,
                    pd.DataFrame(
                        [{
                            "question_type": f"tutorial {tutorial_index + 1}",
                            "Sample_ID": tutorial_index,
                            "Model_name": f"tutorial {tutorial_index + 1}",
                            "question1": answer_list_1[0],
                            "questions2": answer_list_2[0]
                            }]
                            )],ignore_index=True)
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)
                st.session_state.tutorial_index += 1
                st.session_state.page = "Listening test 1" if tutorial_index == 0 else "Listening test 2"
                st.session_state.ratings[dict_name1][st.session_state.tutorial_index] = answer_list_1
                st.session_state.ratings[dict_name2][st.session_state.tutorial_index] = answer_list_2                
                st.rerun()
            else:
                user_ratings_df.loc[
                    (user_ratings_df["Sample_ID"] == tutorial_index) &
                    (user_ratings_df["question_type"] == f"tutorial {tutorial_index + 1}") &
                    (user_ratings_df["Model_name"] == f"tutorial {tutorial_index + 1}"), "question1"] =     st.session_state.ratings[dict_name1][st.session_state.tutorial_index] = answer_list_1[0]
                user_ratings_df.loc[
                    (user_ratings_df["Sample_ID"] == tutorial_index) &
                    (user_ratings_df["question_type"] == f"tutorial {tutorial_index + 1}") &
                    (user_ratings_df["Model_name"] == f"tutorial {tutorial_index + 1}"), "question2"] = answer_list_2[0]
                st.session_state.ratings[dict_name1][st.session_state.tutorial_index] = answer_list_1
                st.session_state.ratings[dict_name2][st.session_state.tutorial_index] = answer_list_2

elif st.session_state.page == "Listening test 1":
    model_id = {0: "SteerEdit", 1: "MusicMagus", 2: "ZETA", 3: "DDIM",4: "SDEdit" }
    st.session_state.question_type = 'test1'

    # Get current question audio files
    audio_files = audio_questions[st.session_state.test_index]
    assert len(set(os.path.dirname(f) for f in audio_files)) == 1, "Not all files are in the same directory!"

    # Display listener ID
    st.write(f'Listener ID: {st.session_state.listener_id}')
    st.write("#### Source Music")
    st.audio(audio_files[0], format="audio/flac")

    # Read text file
    with open(audio_files[1], "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    
    source_prompt = re.findall(r'\[(.*?)\]', lines[1])
    target_prompt = re.findall(r'\[(.*?)\]', lines[2])
    st.write(f"##### Edit Instruction: Edit the source **{source_prompt}** music to a **{target_prompt}** music.")

    # Initialize rating lists
    answer_list_1, answer_list_2 = [], []
    
    # Display edited results and rating buttons
    for i, audio_file in enumerate(audio_files[2:], start=1):
        st.write(f"#### Edited result {i}")
        st.audio(audio_file, format="audio/flac")

        answer_list_1.append(render_rating_buttons(
            5, f"Question {2 * i - 1}:",
            "Please rate how well the content (e.g., melody and vocal elements) remains consistent with the source music.",
            i - 1, st.session_state.test_index,
            st.session_state.ratings['p1_q1'], "test1q1"
        ))

        answer_list_2.append(render_rating_buttons(
            5, f"Question {2 * i}:",
            f"Please rate how well the edited result matches the style of **{target_prompt}**.",
            i - 1, st.session_state.test_index,
            st.session_state.ratings['p1_q2'], "test1q2"
        ))
    # Completion Messages
    if st.session_state.test_completed:
        if not st.session_state.test_completed2:
            st.success("#### Thank you for completing part 1 of the test! You can review/edit your ratings.")
        else:
            st.success("#### Thank you for completing everything! You can close the browser or review your ratings.")

    # Progress Bar
    st.write("### Progress")
    num_cols = 5
    cols = st.columns(num_cols)
    for idx, _ in enumerate(audio_questions):
        completed = idx in st.session_state.ratings['p1_q1']
        is_current = idx == st.session_state.test_index
        status = "✅" if completed and not is_current else "▶️" if is_current else "⬜"
        with cols[idx % num_cols]:
            if st.button(f"{status} {idx+1}", key=f"progress_{idx}"):
                st.session_state.test_index = idx
                st.rerun()

    # Submit Ratings
    if st.button("Submit Ratings"):
        sample_id = audio_questions[st.session_state.test_index][0].split("/")[1]
        
        if len([x for x in answer_list_1 if x is not None]) < 5 or len([x for x in answer_list_2 if x is not None]) < 5:
            st.error("Please select your rating before proceeding.")
        else:
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)
            if st.session_state.test_index not in st.session_state.ratings['p1_q1']:
                for idx, (a, b) in enumerate(zip(answer_list_1, answer_list_2)):
                    new_entry = pd.DataFrame([{
                        "question_type": 'test1',
                        "Sample_ID": sample_id,
                        "Model_name": model_id[idx],
                        "question1": a,
                        "question2": b,
                    }])
                    user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)
                
                st.session_state.ratings['p1_q1'][st.session_state.test_index] = answer_list_1
                st.session_state.ratings['p1_q2'][st.session_state.test_index] = answer_list_2
            else:
                for idx, (a, b) in enumerate(zip(answer_list_1, answer_list_2)):
                    user_ratings_df.loc[
                        (user_ratings_df["Sample_ID"] == sample_id) &
                        (user_ratings_df["question_type"] == "test1") &
                        (user_ratings_df["Model_name"] == model_id[idx]), "question1"] = a
                    user_ratings_df.loc[
                        (user_ratings_df["Sample_ID"] == sample_id) &
                        (user_ratings_df["question_type"] == "test1") &
                        (user_ratings_df["Model_name"] == model_id[idx]), "question2"] = b
                
                st.session_state.ratings['p1_q1'][st.session_state.test_index] = answer_list_1
                st.session_state.ratings['p1_q2'][st.session_state.test_index] = answer_list_2
            
            if len(st.session_state.ratings['p1_q1']) >= len(audio_questions):
                st.session_state.page = "Tutorial 2"
                st.session_state.test_completed = True
                finish_time = datetime.datetime.now()
                if "finish_time" not in user_ratings_df.columns:
                    user_ratings_df["finish_time"] = None
                user_ratings_df.at[0, "finish_time"] = finish_time
            
            user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)
            
            for i in range(len(audio_questions)):
                if i not in st.session_state.ratings['p1_q1']:
                    st.session_state.test_index = i
                    st.rerun()
                    break
            st.rerun()

elif st.session_state.page == "Listening test 2":
    # set question type for csv logging
    st.session_state.question_type = 'test2'

    model_id = {0: "SteerMusic", 1: "textinv", 2: "DreamSound" }

    # Show progress bar with clickable selection
    st.write("### Progress")
    num_cols = 5
    cols = st.columns(num_cols)
    for idx, _ in enumerate(audio_questions2):
        completed = idx in st.session_state.ratings['p2_q1']
        is_current = idx == st.session_state.test_index2
        status = "✅" if completed and not is_current else "▶️" if is_current else "⬜"
        with cols[idx % num_cols]:
            if st.button(f"{status} {idx+1}", key=f"progress_{idx}"):
                st.session_state.test_index2 = idx
                st.rerun()

    # Get current question audio files
    audio_files = audio_questions2[st.session_state.test_index2]
    # make sure there is no error in sample name
    assert len(set(os.path.dirname(f) for f in audio_files)) == 1, \
        "Not all files are in the same directory!"    

    # read txt file
    with open(audio_files[1], "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # Remove empty lines and strip whitespace    

    # Display audio in a grid layout
    st.write(f'Listener ID: {st.session_state.listener_id}')
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### Source")
        st.audio(audio_files[0], format="audio/flac")
        # st.write(f"##### source prompt")
        # st.write(f"{lines[0]}")
    with col2:
        concept_label = get_label_from_folder(os.path.dirname(audio_files[0]))
        st.write(f"#### Reference: {concept_label}")
        st.audio(audio_files[2], format="audio/flac")
        # st.write(f"##### target prompt")
        # st.write(re.sub(r'\[.*?\]', f"[{concept_label}]", lines[0]))   
        # 
    source_prompt = re.findall(r'\[(.*?)\]', lines[0])
    st.write("#### Edit instruction:")
    st.write(f"Edit the source {source_prompt} music to a {concept_label} music according to the reference music.")    
    
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.write("#### edited result 1")
    #     st.audio(audio_files[3], format="audio/flac")
    # with col2:
    #     st.write("#### edited result 2")
    #     st.audio(audio_files[4], format="audio/flac")

    answer_list_1 = []
    answer_list_2 = []

    # Display edited results and rating buttons
    for i, audio_file in enumerate(audio_files[3:], start=1):
        st.write(f"#### Edited result {i}")
        st.audio(audio_file, format="audio/flac")

        answer_list_1.append(render_rating_buttons(
            5, f"Question {2 * i - 1}:",
            "Please rate how well the content (e.g., melody and vocal elements) remains consistent with the source music.",
            i - 1, st.session_state.test_index2,
            st.session_state.ratings['p2_q1'], "test2q1"
        ))

        answer_list_2.append(render_rating_buttons(
            5, f"Question {2 * i}:",
            f"Please rate how well the edited result matches the style of **{concept_label}**.",
            i - 1, st.session_state.test_index2,
            st.session_state.ratings['p2_q2'], "test2q2"
        ))    

    # Completion Messages
    if st.session_state.test_completed2:
        if not st.session_state.test_completed:
            st.success("#### Thank you for completing part 2 of the test! You can review/edit your ratings and proceed to part 1")
        else:
            st.success("#### Thank you for completing everything! You can close the browser or review your ratings.")

    if st.button("Submit Ratings"):
        sample_id = audio_questions2[st.session_state.test_index2][0].split("/")[1]
        
        if len([x for x in answer_list_1 if x is not None]) < 3 or len([x for x in answer_list_2 if x is not None]) < 3:
            st.error("Please select your rating before proceeding.")
        else:
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)
            
            if st.session_state.test_index2 not in st.session_state.ratings['p2_q1']:
                for idx, (a, b) in enumerate(zip(answer_list_1, answer_list_2)):
                    new_entry = pd.DataFrame([{
                        "question_type": 'test2',
                        "Sample_ID": sample_id,
                        "Model_name": model_id[idx],
                        "question1": a,
                        "question2": b,
                    }])
                    user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)
                
                st.session_state.ratings['p2_q1'][st.session_state.test_index2] = answer_list_1
                st.session_state.ratings['p2_q2'][st.session_state.test_index2] = answer_list_2
            else:
                for idx, (a, b) in enumerate(zip(answer_list_1, answer_list_2)):                
                    user_ratings_df.loc[
                        (user_ratings_df["Sample_ID"] == sample_id) &
                        (user_ratings_df["question_type"] == "test2") &
                        (user_ratings_df["Model_name"] == model_id[idx]), "question1"] = a
                    user_ratings_df.loc[
                        (user_ratings_df["Sample_ID"] == sample_id) &
                        (user_ratings_df["question_type"] == "test2") &
                        (user_ratings_df["Model_name"] == model_id[idx]), "question2"] = b
                
                st.session_state.ratings['p2_q1'][st.session_state.test_index2] = answer_list_1
                st.session_state.ratings['p2_q2'][st.session_state.test_index2] = answer_list_2
            
            if len(st.session_state.ratings['p2_q1']) >= len(audio_questions2):
                st.session_state.test_completed2 = True
                finish_time = datetime.datetime.now()
                if "finish_time" not in user_ratings_df.columns:
                    user_ratings_df["finish_time"] = None
                user_ratings_df.at[0, "finish_time"] = finish_time
            
            user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)
            
            for i in range(len(audio_questions2)):
                if i not in st.session_state.ratings['p2_q1']:
                    st.session_state.test_index2 = i
                    st.rerun()
                    break
            st.rerun()