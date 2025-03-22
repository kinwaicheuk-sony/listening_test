import streamlit as st
import pandas as pd
import os
import uuid
import datetime
import json

# Constants
RATINGS_DIR = "user_ratings"
os.makedirs(RATINGS_DIR, exist_ok=True)

# Load audio paths from JSON
with open("audio_questions.json", "r") as f:
    audio_config = json.load(f)

tutorial_questions = audio_config["tutorial_questions"]
audio_questions = audio_config["audio_questions"]

# Initialize session state
def initialize_session_state():
    if "ratings" not in st.session_state:
        st.session_state.ratings = {}  # Store ratings per question
        st.session_state.ratings_tutorial = {}

    if "question_type" not in st.session_state:
        st.session_state.question_type = "tutorial"  # Default to tutorial

    if "user_info_collected" not in st.session_state:
        st.session_state.user_info_collected = False
        st.session_state.listener_id = str(uuid.uuid4())[:8]  # Auto-generate listener ID
        st.session_state.age = None
        st.session_state.music_training_years = None
        st.session_state.tutorial_index = 0  # Track tutorial question index
        st.session_state.test_index = 0  # Track test question index
        st.session_state.test_completed = False
        st.session_state.start_time = datetime.datetime.now()
        st.session_state.selected_ratings = None
        st.session_state.page = "User Info"  # Start with user info page

# Render rating buttons
def render_rating_buttons(num_buttons, label, instruction):
    st.write(f"##### {label}")

    # Determine the index and log dictionary based on question type
    index = st.session_state.tutorial_index if st.session_state.question_type == "tutorial" else st.session_state.test_index
    log_dict = st.session_state.ratings_tutorial if st.session_state.question_type == "tutorial" else st.session_state.ratings

    # Retrieve previous selection if it exists
    previous_selection = log_dict.get(index, None)

    # Use a temporary variable to hold the selection
    selected_option = st.radio(
        f" {instruction}",
        options=list(range(num_buttons)),
        format_func=lambda x: f"Edit {x + 1}",
        index=previous_selection if previous_selection is not None else None,
        key=f"radio_{label}"
    )

    # Only update session state if the selection has changed
    if log_dict.get(index) != selected_option:
        log_dict[index] = selected_option
        st.session_state.selected_ratings = selected_option
        st.rerun()  # Force re-rendering immediately

# Save user ratings to CSV
def save_user_ratings(question_type, question_index, selected_rating):
    user_ratings_file = os.path.join(RATINGS_DIR, f"{st.session_state.listener_id}.csv")
    metadata = {
        "listener_id": st.session_state.listener_id,
        "age": st.session_state.age,
        "music_training_years": st.session_state.music_training_years,
        "start_time": st.session_state.start_time
    }

    if not os.path.exists(user_ratings_file):
        metadata_df = pd.DataFrame([metadata])
        metadata_df.to_csv(user_ratings_file, index=False)
    else:
        metadata_df = pd.read_csv(user_ratings_file)

    new_entry = pd.DataFrame([{
        "question_type": question_type,
        "question": question_index,
        "selection": selected_rating,
    }])
    metadata_df = pd.concat([metadata_df, new_entry], ignore_index=True)
    metadata_df.to_csv(user_ratings_file, index=False)

# Update page based on sidebar selection
def update_page():
    st.session_state.page = st.session_state.page_selection

# Main app logic
def main():
    initialize_session_state()

    # Title
    st.title("Audio Rating App")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page_options = ["User Info", "Tutorial 1", "Tutorial 2", "Listening test"]
    current_index = page_options.index(st.session_state.page)
    page_selection = st.sidebar.radio(
        "Current progress", 
        page_options, 
        index=current_index, 
        key="page_selection", 
        on_change=update_page
    )
    st.session_state.page = page_selection

    # Page logic
    if st.session_state.page == "User Info":
        st.write("### Please provide your details before starting the test")
        st.text(f"Your Listener ID: {st.session_state.listener_id}")
        st.session_state.age = st.number_input("Enter your age", min_value=18, max_value=100, step=1)
        st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)))

        if st.button("Submit & Start Test"):
            if st.session_state.age is None or st.session_state.music_training_years is None:
                st.error("Please fill in all required fields before proceeding.")
            else:
                save_user_ratings("metadata", 0, None)
                st.session_state.user_info_collected = True
                st.session_state.page = "Tutorial 1"
                st.success("Information saved! Proceed to the test.")
                st.rerun()

    elif st.session_state.page.startswith("Tutorial"):
        index_page = {0: 'Tutorial 1', 1: 'Tutorial 2'}
        instructions = {
            0: 'Edit 1 preserves the melody in the source better and sounds more like the instrument in the target, so edit 1 should be selected.',
            1: 'Edit 2 preserves the melody in the source better and sounds more like the instrument in the target, so edit 2 should be selected.'
        }
        reverse_index_page = {v: k for k, v in index_page.items()}
        st.session_state.tutorial_index = reverse_index_page.get(st.session_state.page, None)
        st.session_state.question_type = "tutorial"

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

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Edited Result 1")
            st.audio(edited, format="audio/flac")
        with col2:
            st.write("#### Edited Result 2")
            st.audio(edited, format="audio/flac")

        render_rating_buttons(2, "Your Answer", instructions[st.session_state.tutorial_index])

        if st.button("Next"):
            if st.session_state.selected_ratings is None and not st.session_state.test_completed:
                st.error("Please select your rating before proceeding.")
            else:
                save_user_ratings("tutorial", st.session_state.tutorial_index, st.session_state.selected_ratings)
                st.session_state.tutorial_index += 1

                if st.session_state.tutorial_index < len(tutorial_questions):
                    st.session_state.page = index_page[st.session_state.tutorial_index]
                else:
                    st.session_state.page = "Listening test"

                st.session_state.selected_ratings = None
                st.rerun()

    elif st.session_state.page == "Listening test":
        st.write("### Progress")
        cols = st.columns(len(audio_questions))
        st.session_state.question_type = 'test'

        for idx in range(len(audio_questions)):
            completed = idx in st.session_state.ratings
            is_current = idx == st.session_state.test_index
            status = "✅" if completed else "▶️" if is_current else "⬜"

            with cols[idx % 10]:
                if st.button(f"{status} {idx+1}", key=f"progress_{idx}"):
                    st.session_state.test_index = idx
                    st.rerun()

        audio_files = audio_questions[st.session_state.test_index]
        st.write(f'Listener ID: {st.session_state.listener_id}')

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Source")
            st.audio(audio_files[0], format="audio/flac")
        with col2:
            st.write("#### Target")
            st.audio(audio_files[1], format="audio/flac")

        col1, col2 = st.columns(2)
        with col1:
            st.write("#### Edited Result 1")
            st.audio(audio_files[0], format="audio/flac")
        with col2:
            st.write("#### Edited Result 2")
            st.audio(audio_files[1], format="audio/flac")

        if st.session_state.test_completed:
            st.write("### Thank you for completing the test!")
            st.write("#### You can close the browser now.")
            st.write("#### Or you can review/edit your ratings by clicking the progress bar")

        render_rating_buttons(2, f"Question {st.session_state.test_index+1}:", "Which editing is more successful?")

        if st.button("Submit Ratings"):
            if st.session_state.selected_ratings is None:
                st.error("Please select your rating before proceeding.")
            else:
                st.session_state.ratings[st.session_state.test_index] = st.session_state.selected_ratings
                save_user_ratings("test", st.session_state.test_index, st.session_state.selected_ratings)

                if len(st.session_state.ratings) >= len(audio_questions):
                    st.session_state.test_completed = True
                    finish_time = datetime.datetime.now()
                    user_ratings_df = pd.read_csv(os.path.join(RATINGS_DIR, f"{st.session_state.listener_id}.csv"))
                    # Update only the row where both conditions are met
                    user_ratings_df.loc[
                        (user_ratings_df["question"] == st.session_state.test_index) & 
                        (user_ratings_df["question_type"] == "test"), 
                        "selection"
                    ] = st.session_state.selected_ratings
                    user_ratings_df.at[0, "finish_time"] = finish_time
                    user_ratings_df.to_csv(os.path.join(RATINGS_DIR, f"{st.session_state.listener_id}.csv"), index=False)
                else:
                    for i in range(len(audio_questions)):
                        if i not in st.session_state.ratings:
                            st.session_state.test_index = i
                            break

                st.session_state.selected_ratings = None
                st.rerun()

if __name__ == "__main__":
    main()