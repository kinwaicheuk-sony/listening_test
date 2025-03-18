import streamlit as st
import pandas as pd
import os
import uuid

# Directory to store user ratings
ratings_dir = "user_ratings"
os.makedirs(ratings_dir, exist_ok=True)

# Store ratings in session state
if "ratings" not in st.session_state:
    st.session_state.ratings = {}  # Store ratings per audio file

if "user_info_collected" not in st.session_state:
    st.session_state.user_info_collected = False
    st.session_state.listener_id = str(uuid.uuid4())[:8]  # Auto-generate listener ID
    st.session_state.age = None
    st.session_state.music_training_years = None
    st.session_state.audio_index = 0  # Track current audio
    st.session_state.test_completed = False  # Track if test is completed
    st.session_state.current_rating = 3  # Default slider value

# Audio file paths
audio_files = [
    [    "/home/tda/projects/project_mfmt_attribution/references/fsat_kw/attribution_result/cross_attn_1e-06/top10/0_train_chunk_id_25378.mp3",
    "/home/tda/projects/project_mfmt_attribution/references/fsat_kw/attribution_result/cross_attn_1e-06/top10/1_train_chunk_id_129190.mp3",
    "/home/tda/projects/project_mfmt_attribution/references/fsat_kw/attribution_result/cross_attn_1e-06/top10/7_train_chunk_id_66396.mp3"
    ] 
]

# Title
st.title("Audio Rating App")

if not st.session_state.user_info_collected:
    st.write("### Please provide your details before starting the test")
    st.text(f"Your Listener ID: {st.session_state.listener_id}")  # Display auto-generated ID
    st.session_state.age = st.number_input("Enter your age", min_value=10, max_value=100, step=1)
    st.session_state.music_training_years = st.selectbox("Years of music training", list(range(51)))
    
    if st.button("Submit & Start Test"):
        st.session_state.user_info_collected = True
        st.success("Information saved! Proceed to the test.")
        st.rerun()
else:
    # Show progress bar with clickable selection
    # Show progress as a list of audio files with visual indicators
    # ==== Highlight version ====
    # Show progress as a list of audio files with visual indicators
    st.write("### Progress")
    cols = st.columns(5)  # Adjust the number of columns as needed
    for idx, file in enumerate(audio_files):
        if file in st.session_state.ratings:
            status = "✅"
        elif idx == st.session_state.audio_index:
            status = "▶️"  # Highlight the current audio being rated
        else:
            status = "⬜"
        
        with cols[idx % 5]:  # Arrange buttons in a row
            if st.button(f"{idx+1} {status} "):
                st.session_state.audio_index = idx
                st.rerun()
    # ===== Slider Bar version =====
    # st.write(f"ID: {st.session_state.listener_id}")
    # st.write(f"### Progress: {sum(file in st.session_state.ratings for file in audio_files)}/{len(audio_files)} completed")
    # selected_index = st.select_slider("Click to jump to the question:", options=list(range(len(audio_files))), value=st.session_state.audio_index, key="audio_selector")
    # if selected_index != st.session_state.audio_index:
    #     st.session_state.audio_index = selected_index
    #     st.rerun()
    
    # Get current audio file
    audio_file_path = audio_files[st.session_state.audio_index]
    
    # Display audio
    st.audio(audio_file_path, format="audio/mp3")

    # Collect rating
    default_rating = st.session_state.ratings.get(audio_file_path, 3)
    rating = st.slider("Rate this audio", 1, 5, default_rating, key=f"rating_slider_{st.session_state.audio_index}")
    
    if st.button("Submit Rating"):
        st.session_state.ratings[audio_file_path] = rating
        
        # Save ratings to a user-specific CSV file
        user_ratings_file = os.path.join(ratings_dir, f"{st.session_state.listener_id}.csv")
        user_df = pd.DataFrame([{ "listener_id": st.session_state.listener_id, "age": st.session_state.age, "music_training_years": st.session_state.music_training_years, "filename": file, "rating": rate} for file, rate in st.session_state.ratings.items()])
        user_df.to_csv(user_ratings_file, index=False)
        
        # Move to next audio only if all files are rated
        if len(st.session_state.ratings) >= len(audio_files):
            st.session_state.test_completed = True
        else:
            st.session_state.audio_index = (st.session_state.audio_index + 1) % len(audio_files)
        
        st.rerun()
    
    # Ensure all ratings are completed before moving to the summary
    if st.session_state.test_completed:
        st.write("## Thank you for completing the test!")
        st.write("### You can close the browse or review/edit your ratings by clicking the progress bar")
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