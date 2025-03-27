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
def render_rating_buttons(num_buttons, label, instruction, index, log, key_prefix):
    """Generalized function to render rating buttons."""
    st.write(f"##### {label}")
    mos_score = {0: "Bad", 1: "Poor", 2: "Fair", 3: "Good", 4: "Excellent"}

    # Retrieve previous selection if it exists
    previous_selections = log.get(st.session_state.test_index, None)
    previous_selection = previous_selections[index] if previous_selections is not None else None

    # Render radio buttons
    selected_option = st.radio(
        f" {instruction}",
        options=list(range(num_buttons)),
        format_func=lambda x: f"{x + 1}: {mos_score[x]}",
        index=previous_selection if previous_selection is not None else None,
        key=f"{key_prefix}_{label}_{st.session_state.test_index}"
    )

    return selected_option



# ========== Parameters Initalization ============
# store ratings in session state
# activate only once
if "ratings" not in st.session_state:
    st.session_state.ratings = {}  # Store ratings per question    
    # for part 1 
    st.session_state.ratings["p1_q1"] = {}
    st.session_state.ratings["p1_q2"] = {}
    # for part 2    
    st.session_state.ratings["p2_q1"] = {}
    st.session_state.ratings["p2_q2"] = {}
    st.session_state.ratings_tutorial = {}

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

# Title
st.title("Audio Rating App")

# Sidebar Navigation
st.sidebar.title("Navigation")
page_options = ["User Info", "Tutorial 1", "Listening test 1", "Tutorial 2",  "Listening test 2"]

# Ensure session state page matches available options
# st.session_state.page = valid_page_mapping.get(st.session_state.page, "User Info")  # Default to 'User Info'
current_index = page_options.index(st.session_state.page)
# Sidebar radio but **DO NOT override manually set page**
# page_selection = st.sidebar.radio("Current progress", page_options, index=current_index)
page_selection = st.sidebar.radio(
    "Current progress", 
    page_options, 
    index=current_index, 
    key="page_selection", 
    on_change=update_page  # Call function when selection changes
)

# FIX: Make sure session state updates to match user selection
st.session_state.page = page_selection  # Update session state to match sidebar selection

if st.session_state.page == "User Info": 
    st.write("### Information for users")
    st.write("This project aims to develop generative AI techniques for music style editing. \
              This could be used by composers or users to edit music tracks into other musical style.    \n\
              The goal of this study is to evaluate two aspects of edited music that we have created using our generative AI system:    \n\
              1. **Correspondence**: How the edited result preserves the main musical contents (e.g., melody and vocal content) on the source music?   \n\
              2. **Style Consistency**: How the edited result align precisely with the desired target style indicated in the brackets on the source and target prompts (e.g., [jazz] → [pop])?    \n\
              In this study, you will listen to five edited results for each question.    \n\
              **Please rate each edited sample according to the questtions.**")
    st.write("### Please provide your details before starting the test")
    st.text(f"Your Listener ID: {st.session_state.listener_id}")  # Display auto-generated ID
    st.session_state.age = st.number_input("Enter your age", min_value=18, max_value=100, step=1)
    if 'music_training_years' not in st.session_state:
        st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)))
    else:
        st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)), st.session_state.music_training_years)        
        
    
    if st.button("Submit & Start Test"):
        if st.session_state.age is None or st.session_state.music_training_years is None:
            st.error("Please fill in all required fields before proceeding.")
        else:
            if not st.session_state.test_completed:
                # Save metadata to CSV at the beginning
                user_ratings_file = os.path.join(ratings_dir, f"{st.session_state.listener_id}.csv")
                metadata = {
                    "listener_id": st.session_state.listener_id,
                    "age": st.session_state.age,
                    "music_training_years": st.session_state.music_training_years,
                    "start_time": st.session_state.start_time
                }
                metadata_df = pd.DataFrame([metadata])
                metadata_df.to_csv(user_ratings_file, index=False)
                st.session_state.user_ratings_file = user_ratings_file  # Store in session
                
                st.session_state.user_info_collected = True
                # st.session_state.page = "Tutorial 1"  # Move to the first tutorial
                st.session_state.page = "Listening test 1"  # Move to the first tutorial
                st.success("Information saved! Proceed to the test.")
            elif st.session_state.test_completed:
                # Modifying existing data when the test is completed
                finish_time = datetime.datetime.now()

                # Load existing data
                user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

                # Update anything the listener changed
                user_ratings_df.at[0, "finish_time"] = finish_time
                user_ratings_df.at[0, "age"] = st.session_state.age
                user_ratings_df.at[0, "music_training_years"] = st.session_state.music_training_years
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)
            else:
                raise ValueError('Case not considered')    

            st.rerun()

elif st.session_state.page.startswith("Tutorial"):
    # manually encode page-index mapping
    index_page = {
        0: 'Tutorial 1',
        1: 'Tutorial 2'
        }
    instructions = {
        0: "This edit attempts to transfer a [**piano**] source music to a [**flute**] music.   \n\
            For each of Question 1 and Question 2, you will be asked to provide a rating from 1 (Bad) to 5 (Excellent). \n\
            The rating scale as below:",
        1: "This edit attempts to transfer a [**piano**] source music to a [**bouzouki**] music according to the [**bouzouki**] reference. \n\
            For each of Question 1 and Question 2, you will be asked to provide a rating from 1 (Bad) to 5 (Excellent).   \n\
            The rating scale as below:"
    }
    titles = {
        0: 'This tutorial introduces Text-based Editing and will guide you through the next 5 questions.',
        1: 'This tutorial introduces Reference-based Editing and will guide you through the next 5 questions.'
    }
    reverse_index_page = {v: k for k, v in index_page.items()}
    # get index from page name
    st.session_state.tutorial_index = reverse_index_page.get(st.session_state.page, None)    

    st.session_state.question_type = "tutorial" # for logging
    # TODO: this only works when there are two questions for tutorial
    # Need to make it more general
    # st.session_state.tutorial_index = 0 if st.session_state.page == "tutorial1" else 1
    # st.session_state.tutorial_index = tutorial_index

    # fetch audio from the list
    # source, target, edited = tutorial_questions[st.session_state.tutorial_index]
    file_paths = tutorial_questions[st.session_state.tutorial_index]

    st.write(f"#### Tutorial {st.session_state.tutorial_index + 1}: {titles[st.session_state.tutorial_index]}")
    st.write(f'Listener ID: {st.session_state.listener_id}')
    if st.session_state.tutorial_index == 0:
        st.write("#### source")
        st.audio(file_paths[0], start_time=0, format="audio/flac")
        st.write("##### Edit instruction")
        st.write("Edit the source **piano** music to a **flute** music.")
        # st.write("##### target prompt")        
        # st.write("A famous classicial music played on a [**flute**]")   
        # col1, col2 = st.columns(2)
        # with col1:
        st.write("#### edited result")
        st.audio(file_paths[1], format="audio/flac")
        
        st.write("Please rate the edited result from 1-Bad to 5-Excellent according to belows questions:")
        st.write("#### Question 1:")
        st.write("Please rate how well does the content of the edited result (e.g., melody and vocal elements) remain consistent with the source music?")
        st.write("#### Question 2:")
        st.write("Please rate how well the edited result matches the style of **flute**?")
    
        # with col2:
        #     st.write("#### edited result 2")
        #     st.audio(file_paths[2], format="audio/flac")             
    elif st.session_state.tutorial_index == 1:
        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Source")
            st.audio(file_paths[0], format="audio/flac")
            st.write("##### source prompt")
            st.write("A famous classicial music played on a [**piano**]")
        with col2:
            st.write("#### Reference: Bouzouki")
            st.audio(file_paths[1], format="audio/flac")
            st.write("##### Target prompt")
            st.write("A famous classicial music played on a [**bouzouki**]")            
        col1, col2 = st.columns(2)
        with col1:
            st.write("#### edited result 1")
            st.audio(file_paths[2], format="audio/flac")
        with col2:
            st.write("#### edited result 2")
            st.audio(file_paths[3], format="audio/flac")                
    else:
        raise ValueError('Case not considered')


    # st.write("### Edited Result")
    # st.audio(edited, format="audio/flac")


    # create buttons
    render_rating_buttons1(
        5,
        "Your Anwser",
        instructions[st.session_state.tutorial_index],
        1
        )

    if st.button("Next"): # determines how many tutorials there are
        finish_time = datetime.datetime.now()
        if st.session_state.selected_ratings == None and st.session_state.test_completed != True:
            st.error("Please select your rating before proceeding.")
        elif st.session_state.selected_ratings == None and st.session_state.test_completed == True:
            st.error("Rating not changed.")
        else:
            # Load existing data
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)
            if not st.session_state.test_completed:
                # Append a new row if question does not exist
                new_entry = pd.DataFrame([{
                    "question_type": 'tutorial',
                    "question": st.session_state.tutorial_index,
                    "selection": st.session_state.selected_ratings,
                }])
                user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)

                # Save back to CSV (overwrite the file)
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)
            elif st.session_state.test_completed:
                # Update only the row where both conditions are met
                user_ratings_df.loc[
                    (user_ratings_df["question"] == st.session_state.tutorial_index) & 
                    (user_ratings_df["question_type"] == "tutorial"), 
                    "selection"
                ] = st.session_state.selected_ratings

                # Check if finish_time column exists, if not, add it
                if "finish_time" in user_ratings_df.columns:
                    user_ratings_df.at[0, "finish_time"] = finish_time  # Update the first row
                else:
                    user_ratings_df["finish_time"] = None  # Create column if missing
                    user_ratings_df.at[0, "finish_time"] = finish_time  # Assign value

                # Save back to CSV (overwrite the file)
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)                


            st.session_state.tutorial_index += 1
            if st.session_state.tutorial_index < len(tutorial_questions):
                # if there are still tutorial questions
                # st.session_state.page = index_page[st.session_state.tutorial_index]  # Move to next page
                st.session_state.page = "Listening test 1"  # Go to test1 after tutorial 1   
            elif st.session_state.tutorial_index == len(tutorial_questions):
                # st.session_state.page = "Listening test 1"  # Move to the test
                st.session_state.page = "Listening test 2"  # Keep tutorial 2 leading to test2                
            else:
                raise ValueError('Unexpected case')
            
            # reset value before next page
            st.session_state.selected_ratings = None
            st.rerun()

elif st.session_state.page == "Listening test 1":
    st.session_state.question_type = 'test1'
    print(f"***{st.session_state.ratings['p1_q1'].keys()=}")

    # Get current question audio files
    audio_files = audio_questions[st.session_state.test_index]
    # make sure there is no error in sample name
    assert len(set(os.path.dirname(f) for f in audio_files)) == 1, \
        "Not all files are in the same directory!"

    # Display audio in a grid layout
    st.write(f'Listener ID: {st.session_state.listener_id}')
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.write("#### source")
    #     st.audio(audio_files[0], format="audio/flac")
    # with col2:
    #     st.write("#### target")
    #     st.audio(audio_files[1], format="audio/flac")
    st.write("#### Source Music")
    st.audio(audio_files[0], start_time=0, format="audio/flac")

    # read txt file
    with open(audio_files[1], "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]  # Remove empty lines and strip whitespace

    st.write("##### Edit instruction")
    source_prompt = re.findall(r'\[(.*?)\]', lines[1])
    target_prompt = re.findall(r'\[(.*?)\]', lines[2])
    st.write(f"Edit the source **{source_prompt}** music to a **{target_prompt}** music.")
    # st.write(lines[1])
    # st.write("##### target prompt")        
    # st.write(lines[2])
    
    col1, col2 = st.columns(2)

    answer_list_1 = [] # melody
    answer_list_2 = [] # style
    local_dict1 = {} # store listner choices
    local_dict2 = {}

    st.write("#### Edited result 1")
    st.audio(audio_files[2], format="audio/flac")
    
    # Loop-based approach to eliminate redundant calls
    answer_list_1, answer_list_2 = [], []

    for i, audio_file in enumerate(audio_files[2:], start=1):  # Skipping first two files if needed
        st.write(f"#### Edited result {i}")
        st.audio(audio_file, format="audio/flac")

        result1 = render_rating_buttons(
            5,
            f"Question {2 * i - 1}:",
            "Please rate how well does the content of the edited result (e.g., melody and vocal elements) remain consistent with the source music?",
            i - 1,
            st.session_state.ratings['p1_q1'],
            "radio1"
        )
        answer_list_1.append(result1)

        result2 = render_rating_buttons(
            5,
            f"Question {2 * i}:",
            f"Please rate how well the edited result matches the style of **{target_prompt}**?",
            i - 1,
            st.session_state.ratings['p1_q2'],
            "radio2"
        )
        answer_list_2.append(result2)

    # Dislay this message when the test is completed
    # if st.session_state.test_completed:
    #     st.success("### Thank you for completing part 1 of the test!")
    #     st.success("#### You can review/edit your ratings in this part")      
    if (st.session_state.test_completed2!=True) and st.session_state.test_completed:
        st.success(
            """
            #### Thank you for completing part 1 of the test!  
            ##### You can review/edit your ratings in this part.
            """
        )
    elif (st.session_state.test_completed2==True) and st.session_state.test_completed:
        st.success(
            """
            #### Thank you for completing everything!  
            ##### You can close the browser now.  
            ##### Or you can review/edit your ratings by clicking the progress bar
            """
        )        
    
    # # Collect ratings
    # default_ratings = st.session_state.ratings.get(st.session_state.test_index, [3, 3, 3])


    # # create buttons
    # render_rating_buttons(
    #     2,
    #     f"Question {st.session_state.test_index+1}:",
    #     "Which edited result better preserves the original melody and vocal content from the source while successfully changing the musical style or instrument indicated in the brackets?")

    model_id = {0: "SteerEdit", 1: "MusicMagus", 2: "ZETA", 3: "DDIM",4: "SDEdit" }
    # Show progress bar with clickable selection
    st.write("### Progress")
    num_cols = 5
    cols = st.columns(num_cols)  # Adjust column count    
    for idx in range(len(audio_questions)):
        print(f"****** {(idx in st.session_state.ratings['p1_q1'].keys())=}")
        completed = idx in st.session_state.ratings['p1_q1'].keys()  # Check if the question has been rated
        is_current = idx == st.session_state.test_index  # Check if it's the current question

        if completed and not is_current:
            status = "✅"  # Completed question
        elif is_current:
            status = "▶️"  # Currently selected question
        else:
            status = "⬜"  # Not answered yet
        
        with cols[idx % num_cols]:  # Arrange in rows
            if st.button(f"{status} {idx+1}", key=f"progress_{idx}"):
                st.session_state.test_index = idx
                st.rerun()
    if st.button("Submit Ratings"):
        sample_id = audio_questions[st.session_state.test_index][0].split("/")[1]
        print(f"button clicked: {st.session_state.ratings['p1_q1'].get(st.session_state.test_index, None)=}")
        non_none_count1 = len([x for x in answer_list_1 if x is not None])
        non_none_count2 = len([x for x in answer_list_2 if x is not None])
        if non_none_count1 < 5 or non_none_count2 < 5:
            st.error("Please select your rating before proceeding.")
        else:
            # check if the question has been answered
            if st.session_state.ratings['p1_q1'].get(st.session_state.test_index, None) == None:
                # Load existing data
                user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

                if not st.session_state.test_completed:
                    for idx, (a, b) in enumerate(zip(answer_list_1, answer_list_2)):
                        # Append a new row if question does not exist
                        new_entry = pd.DataFrame([{
                            "question_type": 'test1',
                            "Sample_ID":  sample_id,
                            "Model_name": model_id[idx],
                            "question1": a,
                            "question2": b,
                        }])
                        print(f"{new_entry=}")
                        user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)

                    # Save back to CSV (overwrite the file)
                    user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)
                # saving answered questions to log_dict
                st.session_state.ratings['p1_q1'][st.session_state.test_index] = answer_list_1
                st.session_state.ratings['p1_q2'][st.session_state.test_index] = answer_list_2
                print(f"{st.session_state.ratings['p1_q1']=}")
                print(f"{len(st.session_state.ratings['p1_q1'])=}")
            # Modifying existing data when the test is completed
            elif st.session_state.ratings['p1_q1'].get(st.session_state.test_index, None) != None:
                # Load existing data
                user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

                # Update only the row where both conditions are met
                for idx, (a, b) in enumerate(zip(answer_list_1, answer_list_2)):                
                    user_ratings_df.loc[
                        (user_ratings_df["Sample_ID"] == sample_id) & 
                        (user_ratings_df["question_type"] == "test1") &
                        (user_ratings_df["Model_name"] == model_id[idx]), 
                        "question1"
                    ] = a

                    user_ratings_df.loc[
                        (user_ratings_df["question2"] == sample_id) & 
                        (user_ratings_df["question_type"] == "test1") &
                        (user_ratings_df["Model_name"] == model_id[idx]), 
                        "question2"
                    ] = b

                # update the log_dict
                st.session_state.ratings['p1_q1'][st.session_state.test_index] = answer_list_1
                st.session_state.ratings['p1_q2'][st.session_state.test_index] = answer_list_2                

                # Check if all questions have been answered in this part
                if len(st.session_state.ratings['p1_q1']) >= len(audio_questions):
                    # st.session_state.page = "Listening test 2"  # Move to the test      
                    st.session_state.page = "Tutorial 2"  # Move to tutorial 2 instead of test2     
                    finish_time = datetime.datetime.now()                    
                    st.session_state.test_completed = True
                    # Check if finish_time column exists, if not, add it
                    if "finish_time" in user_ratings_df.columns:
                        user_ratings_df.at[0, "finish_time"] = finish_time  # Update the first row
                    else:
                        user_ratings_df["finish_time"] = None  # Create column if missing
                        user_ratings_df.at[0, "finish_time"] = finish_time  # Assign value

                # Save back to CSV (overwrite the file)
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)                             

            
            # Move to the next unanswered question
            for i in range(len(audio_questions)):
                print(f"======={st.session_state.ratings['p1_q1'].keys()=}")
                print(f"======={i in st.session_state.ratings['p1_q1'].keys()=}")
                if i not in st.session_state.ratings['p1_q1'].keys():  # Find first unanswered question
                    st.session_state.test_index = i
                    break  # Stop searching once we find an unanswered question                          
            st.session_state.selected_ratings = None
            st.rerun()      


elif st.session_state.page == "Listening test 2":
    # Show progress bar with clickable selection
    st.write("### Progress")
    num_cols = 5
    cols = st.columns(num_cols)  # Adjust column count
    st.session_state.question_type = 'test2'

    for idx in range(len(audio_questions2)):
        completed = idx in st.session_state.ratings2  # Check if the question has been rated
        is_current = idx == st.session_state.test_index2  # Check if it's the current question

        if completed and not is_current:
            status = "✅"  # Completed question
        elif is_current:
            status = "▶️"  # Currently selected question
        else:
            status = "⬜"  # Not answered yet
        
        with cols[idx % num_cols]:  # Arrange in rows
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
    st.write("#### Edited result 1")
    st.audio(audio_files[3], format="audio/flac")
    
    result1 = render_rating_buttons(
        5,
        f"Question 1:",
        "Please rate how well does the content of the edited result (e.g., melody and vocal elements) remain consistent with the source music?")
    answer_list_1.append(result1)
    result2 = render_rating_buttons(
        5,
        f"Question 2:",
        f"Please rate how well the edited result matches the style of **{concept_label}** on the reference music?")
    answer_list_1.append(result2)    
    

    st.write("#### Edited result 2")
    st.audio(audio_files[4], format="audio/flac")
    
    result1 = render_rating_buttons(
        5,
        f"Question 1:",
        "Please rate how well does the content of the edited result (e.g., melody and vocal elements) remain consistent with the source music?")
    answer_list_1.append(result1)
    result2 = render_rating_buttons(
        5,
        f"Question 2:",
        f"Please rate how well the edited result matches the style of **{concept_label}** on the reference music?")
    answer_list_1.append(result2)    

    st.write("#### Edited result 3")
    st.audio(audio_files[5], format="audio/flac")
    
    result1 = render_rating_buttons(
        5,
        f"Question 1:",
        "Please rate how well does the content of the edited result (e.g., melody and vocal elements) remain consistent with the source music?")
    answer_list_1.append(result1)
    result2 = render_rating_buttons(
        5,
        f"Question 2:",
        f"Please rate how well the edited result matches the style of **{concept_label}** on the reference music?")
    answer_list_1.append(result2)    

    # Dislay this message when the test is completed
    if (st.session_state.test_completed!=True) and st.session_state.test_completed2:
        st.success(
            """
            #### Thank you for completing part 2 of the test!  
            ##### You can review/edit your ratings in this part.
            """
        )
    elif (st.session_state.test_completed==True) and st.session_state.test_completed2:
        st.success(
            """
            #### Thank you for completing everything!  
            ##### You can close the browser now.  
            ##### Or you can review/edit your ratings by clicking the progress bar
            """
        )
        # st.success("#### You can close the browser now.")
        # st.success("#### Or you can review/edit your ratings by clicking the progress bar"

    # Collect ratings
    # default_ratings = st.session_state.ratings2.get(st.session_state.test_index2, [3, 3, 3])


    # create buttons
    # render_rating_buttons(
    #     2,
    #     f"Question {st.session_state.test_index2+1}:",
    #     "Which editing sounds closer to the concept in the reference audio while maintaining the content in the source audio?")



    model_id = {0: "SteerMusic", 1: "textinv", 2: "DreamSound" }
    if st.button("Submit Ratings"):
        if st.session_state.selected_ratings == None:
            st.error("Please select your rating before proceeding.")
        else:        
            if tuple(audio_files) not in st.session_state.ratings2:
                st.session_state.ratings2[st.session_state.test_index2] = st.session_state.selected_ratings

                # Load existing data
                user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

                if not st.session_state.test_completed2:
                # Load existing data
                # user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

                # if not st.session_state.test_completed:
                    for idx, (a, b) in enumerate(zip(answer_list_1, answer_list_2)):
                        # Append a new row if question does not exist
                        new_entry = pd.DataFrame([{
                            "question_type": 'test1',
                            "Sample_ID":  audio_questions[0][0].split("/")[1],
                            "Model_name": model_id[idx],
                            "question1": a,
                            "question2": b,
                        }])
                        user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)

                    # Save back to CSV (overwrite the file)
                    user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)    

                    # # Append a new row if question does not exist
                    # new_entry = pd.DataFrame([{
                    #     "question_type": 'test2',
                    #     "question": st.session_state.test_index2,
                    #     "selection": st.session_state.selected_ratings,
                    # }])
                    # user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)

                    # Save back to CSV (overwrite the file)
                    user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)    

            # Modifying existing data when the test is completed
            if len(st.session_state.ratings2) >= len(audio_questions2):
                st.session_state.test_completed2 = True

                finish_time = datetime.datetime.now()

                # Load existing data
                user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

                # Update only the row where both conditions are met
                user_ratings_df.loc[
                    (user_ratings_df["question"] == st.session_state.test_index2) & 
                    (user_ratings_df["question_type"] == "test2"), 
                    "selection"
                ] = st.session_state.selected_ratings

                # Check if finish_time column exists, if not, add it
                if "finish_time" in user_ratings_df.columns:
                    user_ratings_df.at[0, "finish_time"] = finish_time  # Update the first row
                else:
                    user_ratings_df["finish_time"] = None  # Create column if missing
                    user_ratings_df.at[0, "finish_time"] = finish_time  # Assign value

                # Save back to CSV (overwrite the file)
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)

            else:
                # Move to the next unanswered question
                for i in range(len(audio_questions2)):
                    if i not in st.session_state.ratings2:  # Find first unanswered question
                        st.session_state.test_index2 = i
                        break  # Stop searching once we find an unanswered question
            st.session_state.selected_ratings = None
            st.rerun()