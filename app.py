import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os
import datetime
import time
from database import insert_match_data


def MatchDataEntry():

    st.title("Match Data Entry")

    # Match Data Input Fields
    c1,c2,c3=st.columns(3)
    match_id = c1.number_input("Match ID", min_value=1, step=1)
    teams = c2.text_input("Teams")
    location = c3.text_input("Location")
    c1,c2,c3=st.columns(3)
    match_type = c1.text_input("Match Type")
    winner = c2.text_input("Winner")
    match_timestamp = c3.text_input("Match Timestamp format: YYYY-MM-DD HH:MM:SS",value=None)
    # Video upload
    video_file = st.file_uploader("Upload match video", type=["mp4", "mov", "avi", "mkv"])
    if video_file is not None:
        st.info(f"Video will be saved to 'data/videos/{video_file.name}'")
    video_path = f"data/videos/{video_file.name}" if video_file else ""
  

    if st.button("Insert Data") and video_file is not None:
        if match_id and teams and location and match_type and winner and video_file :
            try:
                # Insert data into the database
                insert_match_data(match_id, teams, location, match_type, winner, video_path, match_timestamp)
                # Save the uploaded video file
                with open(video_path, "wb") as f:
                    f.write(video_file.getbuffer())
                st.success("Match data inserted successfully! and video saved.")
                # Display the uploaded video
                st.video(video_file)
            except Exception as e:
                st.error(f"Error inserting data: {e}")
        else:
            st.error("Please fill out all required fields.")

st.navigation([MatchDataEntry],position='top').run()




