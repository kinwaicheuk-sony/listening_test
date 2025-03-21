import streamlit as st
import pandas as pd
import os
import uuid
import datetime

# Directory to store user ratings
ratings_dir = "user_ratings"
os.makedirs(ratings_dir, exist_ok=True)

# refresh page when clicking on the navigation pane
def update_page():
    st.session_state.page = st.session_state.page_selection

# Rating buttons
def render_rating_buttons(num_buttons, label, instruction):
    st.write(f"##### {label}")

    # Determine the index to store ratings
    if st.session_state.question_type == "tutorial":
        index = st.session_state.tutorial_index
        log_dict = st.session_state.ratings_tutorial
    else:
        index = st.session_state.test_index
        log_dict = st.session_state.ratings

    # Retrieve previous selection if it exists
    previous_selection = log_dict.get(index, None)

    # Use a temporary variable to hold the selection
    selected_option = st.radio(
        f" {instruction}",
        options=list(range(num_buttons)),
        format_func=lambda x: f"Edit {x + 1}",
        index=previous_selection if previous_selection is not None else 0,
        key=f"radio_{label}"
    )

    # Only update session state if the selection has changed
    if log_dict.get(index) != selected_option:
        log_dict[index] = selected_option
        st.session_state.selected_ratings = selected_option
        st.rerun()  # Force re-rendering immediately


# ========== Parameters Initalization ============
# store ratings in session state
if "ratings" not in st.session_state:
    st.session_state.ratings = {}  # Store ratings per question
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
    st.session_state.test_completed = False
    st.session_state.start_time = datetime.datetime.now()
    st.session_state.selected_ratings = None
    if "page" not in st.session_state:
        st.session_state.page = "User Info"  # Start with user info page

# ========== End of Parameters Initalization ============

# Audio file paths
tutorial_questions = [
    [
    "audio/flac/source1.flac",
    "audio/flac/source1.flac",
    "audio/flac/source1.flac",
    ],
    [
    "audio/flac/source1.flac",
    "audio/flac/target1.flac",
    "audio/flac/target1.flac",
    ],
]

audio_questions = [
    [
    "audio/flac/source1.flac",
    "audio/flac/target1.flac",
    "audio/flac/edit1_s1_t1.flac"
    ],
    [
    "audio/flac/source1.flac",
    "audio/flac/target1.flac",
    "audio/flac/edit2_s1_t1.flac"
    ],
    [    
    "audio/flac/source1.flac",
    "audio/flac/target2.flac",
    "audio/flac/edit1_s1_t2.flac"
    ],
    [
    "audio/flac/source1.flac",
    "audio/flac/target2.flac",
    "audio/flac/edit2_s1_t2.flac"
    ],
    [
    "audio/flac/source1.flac",
    "audio/flac/target3.flac",
    "audio/flac/edit1_s1_t3.flac"
    ],
    [
    "audio/flac/source1.flac",
    "audio/flac/target3.flac",
    "audio/flac/edit2_s1_t3.flac"
    ],
]

# Title
st.title("Audio Rating App")

# Sidebar Navigation
st.sidebar.title("Navigation")
page_options = ["User Info", "Tutorial 1", "Tutorial 2", "Listening test"]

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
    st.write("### Please provide your details before starting the test")
    st.text(f"Your Listener ID: {st.session_state.listener_id}")  # Display auto-generated ID
    st.session_state.age = st.number_input("Enter your age", min_value=18, max_value=100, step=1)
    if 'music_training_years' not in st.session_state:
        st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)))
    else:
        st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)), st.session_state.music_training_years)        
        
    
    if st.button("Submit & Start Test"):
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
            st.session_state.page = "Tutorial 1"  # Move to the first tutorial
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
        0: 'edit 1 preserves the melody in the source better and sounds more like the instrument in the target, so edit 1 should be selected.',
        1: 'edit 2 preserves the melody in the source better and sounds more like the instrument in the target, so edit 2 should be selected.'
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
    source, target, edited = tutorial_questions[st.session_state.tutorial_index]

    st.write(f"#### Tutorial {st.session_state.tutorial_index + 1}: How to Rate")
    st.write(f'Listener ID: {st.session_state.listener_id}')
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### Source")
        st.audio(source, format="audio/flac")
    with col2:
        st.write("#### Target")
        st.audio(target, format="audio/flac")

    # st.write("### Edited Result")
    # st.audio(edited, format="audio/flac")
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### edited result 1")
        st.audio(edited, format="audio/flac")
    with col2:
        st.write("#### edited result 2")
        st.audio(edited, format="audio/flac")    

    # create buttons
    render_rating_buttons(
        2,
        "Your Anwser",
        instructions[st.session_state.tutorial_index]
        )

    if st.button("Next"): # determines how many tutorials there are
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

        st.session_state.tutorial_index += 1
        if st.session_state.tutorial_index < len(tutorial_questions):
            # if there are still tutorial questions
            st.session_state.page = index_page[st.session_state.tutorial_index]  # Move to next page             
        elif st.session_state.tutorial_index == len(tutorial_questions):
            st.session_state.page = "Listening test"  # Move to the test
        else:
            raise ValueError('Unexpected case')
        

           
        
        st.rerun()

elif st.session_state.page == "Listening test":
    # Show progress bar with clickable selection
    st.write("### Progress")
    cols = st.columns(len(audio_questions))  # Adjust column count
    st.session_state.question_type = 'test'

    for idx in range(len(audio_questions)):
        completed = idx in st.session_state.ratings  # Check if the question has been rated
        is_current = idx == st.session_state.test_index  # Check if it's the current question

        if completed and not is_current:
            status = "✅"  # Completed question
        elif is_current:
            status = "▶️"  # Currently selected question
        else:
            status = "⬜"  # Not answered yet
        
        with cols[idx % 10]:  # Arrange in rows
            if st.button(f"{status} {idx+1}", key=f"progress_{idx}"):
                st.session_state.test_index = idx
                st.rerun()

    # Get current question audio files
    audio_files = audio_questions[st.session_state.test_index]

    # Display audio in a grid layout
    st.write(f'Listener ID: {st.session_state.listener_id}')
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### source")
        st.audio(audio_files[0], format="audio/flac")
    with col2:
        st.write("#### target")
        st.audio(audio_files[1], format="audio/flac")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("#### edited result 1")
        st.audio(audio_files[0], format="audio/flac")
    with col2:
        st.write("#### edited result 2")
        st.audio(audio_files[1], format="audio/flac")

    # Dislay this message when the test is completed
    if st.session_state.test_completed:
        st.write("### Thank you for completing the test!")
        st.write("#### You can close the browser now.")
        st.write("#### Or you can review/edit your ratings by clicking the progress bar")
    
    # Collect ratings
    default_ratings = st.session_state.ratings.get(st.session_state.test_index, [3, 3, 3])


    # create buttons
    render_rating_buttons(
        2,
        f"Question {st.session_state.test_index+1}:",
        "which editing is more successful?")



    
    if st.button("Submit Ratings"):
        if tuple(audio_files) not in st.session_state.ratings:
            st.session_state.ratings[st.session_state.test_index] = st.session_state.selected_ratings

            # Load existing data
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

            if not st.session_state.test_completed:
                # Append a new row if question does not exist
                new_entry = pd.DataFrame([{
                    "question_type": 'test',
                    "question": st.session_state.test_index,
                    "selection": st.session_state.selected_ratings,
                }])
                user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)

                # Save back to CSV (overwrite the file)
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)    

        # Modifying existing data when the test is completed
        if len(st.session_state.ratings) >= len(audio_questions):
            st.session_state.test_completed = True
            finish_time = datetime.datetime.now()

            # Load existing data
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

            # Update only the row where both conditions are met
            user_ratings_df.loc[
                (user_ratings_df["question"] == st.session_state.test_index) & 
                (user_ratings_df["question_type"] == "test"), 
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
            for i in range(len(audio_questions)):
                if i not in st.session_state.ratings:  # Find first unanswered question
                    st.session_state.test_index = i
                    break  # Stop searching once we find an unanswered question
            
        st.rerun()
