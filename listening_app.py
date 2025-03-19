import streamlit as st
import pandas as pd
import os
import uuid
import datetime

# Directory to store user ratings
ratings_dir = "user_ratings"
os.makedirs(ratings_dir, exist_ok=True)

# Store ratings in session state
if "ratings" not in st.session_state:
    st.session_state.ratings = {}  # Store ratings per question

if "user_info_collected" not in st.session_state:
    st.session_state.user_info_collected = False
    st.session_state.listener_id = str(uuid.uuid4())[:8]  # Auto-generate listener ID
    st.session_state.age = None
    st.session_state.music_training_years = None
    st.session_state.question_index = 0  # Track current question
    st.session_state.test_completed = False
    st.session_state.start_time = datetime.datetime.now()
    if "page" not in st.session_state:
        st.session_state.page = "user_info"  # Start with user info page

# Audio file paths
tutorial_questions = [
    [
    "audio/mp3/source1.mp3",
    "audio/mp3/source1.mp3",
    "audio/mp3/source1.mp3",
    [5, 5, 5]
    ],
    [
    "audio/mp3/source1.mp3",
    "audio/mp3/target1.mp3",
    "audio/mp3/target1.mp3",
    [5, 1, 2]
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

if st.session_state.page == "user_info":
    st.write("### Please provide your details before starting the test")
    st.text(f"Your Listener ID: {st.session_state.listener_id}")  # Display auto-generated ID
    st.session_state.age = st.number_input("Enter your age", min_value=10, max_value=100, step=1)
    st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)))
    
    if st.button("Submit & Start Test"):
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
        st.session_state.page = "tutorial1"  # Move to the first tutorial
        st.success("Information saved! Proceed to the test.")
        st.rerun()

elif st.session_state.page.startswith("tutorial"):
    tutorial_index = 0 if st.session_state.page == "tutorial1" else 1
    source, target, edited, default_ratings = tutorial_questions[tutorial_index]

    st.write(f"### Tutorial {tutorial_index + 1}: How to Rate")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("### Source")
        st.audio(source, format="audio/mp3")
    with col2:
        st.write("### Target")
        st.audio(target, format="audio/mp3")

    st.write("### Edited Result")
    st.audio(edited, format="audio/mp3")

    # Predefined tutorial ratings
    score_a = st.slider("### Score A", 1, 5, default_ratings[0], key=f"tutorial_score_a_{tutorial_index}")
    score_b = st.slider("### Score B", 1, 5, default_ratings[1], key=f"tutorial_score_b_{tutorial_index}")
    score_c = st.slider("### Score C", 1, 5, default_ratings[2], key=f"tutorial_score_c_{tutorial_index}")

    if st.button("Next"): # determines how many tutorials there are
        if tutorial_index == 0:
            st.session_state.page = "tutorial2"  # Move to second tutorial
        else:
            st.session_state.page = "test"  # Move to the test
        st.rerun()

elif st.session_state.page == "test":
    # Show progress bar with clickable selection
    # Show progress as a list of audio files with visual indicators
    # ==== Highlight version ====
    # Show progress as a list of audio files with visual indicators
    st.write("### Progress")
    cols = st.columns(len(audio_questions))  # Adjust column count

    for idx in range(len(audio_questions)):
        completed = idx in st.session_state.ratings  # Check if the question has been rated
        status = "✅" if completed else ("▶️" if idx == st.session_state.question_index else "⬜")
        
        with cols[idx % 5]:  # Arrange in rows
            if st.button(f"{status} {idx+1}", key=f"progress_{idx}"):
                st.session_state.question_index = idx
                st.rerun()
    # ===== Slider Bar version =====
    # st.write(f"ID: {st.session_state.listener_id}")
    # st.write(f"### Progress: {sum(file in st.session_state.ratings for file in audio_files)}/{len(audio_files)} completed")
    # selected_index = st.select_slider("Click to jump to the question:", options=list(range(len(audio_files))), value=st.session_state.audio_index, key="audio_selector")
    # if selected_index != st.session_state.audio_index:
    #     st.session_state.audio_index = selected_index
    #     st.rerun()
    
    # Get current question audio files
    audio_files = audio_questions[st.session_state.question_index]
    
    # Display audio in a grid layout
    st.write(f'Listener ID: {st.session_state.listener_id}')
    col1, col2 = st.columns(2)
    with col1:
        st.write("### source")
        st.audio(audio_files[0], format="audio/mp3")
    with col2:
        st.write("### target")
        st.audio(audio_files[1], format="audio/mp3")
    
    st.write("### edited result")
    st.audio(audio_files[2], format="audio/mp3")
    
    # Collect ratings
    default_ratings = st.session_state.ratings.get(st.session_state.question_index, [3, 3, 3])
    score_a = st.slider("### Score A", 1, 5, default_ratings[0], key=f"score_a_{st.session_state.question_index}")
    score_b = st.slider("### Score B", 1, 5, default_ratings[1], key=f"score_b_{st.session_state.question_index}")
    score_c = st.slider("### Score C", 1, 5, default_ratings[2], key=f"score_c_{st.session_state.question_index}")
    
    if st.button("Submit Ratings"):
        if tuple(audio_files) not in st.session_state.ratings:
            st.session_state.ratings[st.session_state.question_index] = [score_a, score_b, score_c]

            # Load existing data
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)

            if not st.session_state.test_completed:
                # Append a new row if question does not exist
                new_entry = pd.DataFrame([{
                    "question": st.session_state.question_index,
                    "Score A": score_a,
                    "Score B": score_b,
                    "Score C": score_c,
                }])
                user_ratings_df = pd.concat([user_ratings_df, new_entry], ignore_index=True)

                # Save back to CSV (overwrite the file)
                user_ratings_df.to_csv(st.session_state.user_ratings_file, index=False)    

        if len(st.session_state.ratings) >= len(audio_questions):
            st.session_state.test_completed = True
            finish_time = datetime.datetime.now()

            # Load existing data
            user_ratings_df = pd.read_csv(st.session_state.user_ratings_file)


            user_ratings_df.loc[user_ratings_df["question"] == st.session_state.question_index, ["Score A", "Score B", "Score C"]] = [score_a, score_b, score_c]

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
                    st.session_state.question_index = i
                    break  # Stop searching once we find an unanswered question
            
        st.rerun()
    
    # Ensure all ratings are completed before moving to the summary
    if st.session_state.test_completed:
        st.write("## Thank you for completing the test!")
        st.write("### You can close the browser now.")
        st.write("### Or you can review/edit your ratings by clicking the progress bar")
        # user_ratings_file = os.path.join(ratings_dir, f"{st.session_state.listener_id}.csv")
        # if os.path.exists(user_ratings_file):
        #     user_ratings_df = pd.read_csv(user_ratings_file)
        #     st.write("### Your Submitted Ratings")
        #     st.dataframe(user_ratings_df)
            
        #     # Allow users to modify their ratings and re-listen
        #     st.write("### Modify Your Ratings")
        #     for i, entry in user_ratings_df.iterrows():
        #         st.audio(entry['filename'], format="audio/mp3")
        #         new_rating = st.slider(f"Modify rating for {entry['filename']}", 1, 5, entry["rating"], key=f"modify_rating_{i}")
        #         user_ratings_df.at[i, "rating"] = new_rating
            
        #     if st.button("Save Changes"):
        #         user_ratings_df.to_csv(user_ratings_file, index=False)
        #         st.success("Your changes have been saved!")