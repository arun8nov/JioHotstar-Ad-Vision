import streamlit as st
import mysql.connector
from dotenv import load_dotenv
import os
from database import insert_match_data


def MatchDataEntry():

    st.title("Match Data Entry")

    c1,c2,c3=st.columns(3)
    match_id = c1.number_input("Match ID", min_value=1, step=1)
    teams = c2.text_input("Teams")
    location = c3.text_input("Location")
    c1,c2,c3,c4=st.columns(4)
    match_type = c1.text_input("Match Type")
    winner = c2.text_input("Winner")
    video_path = c3.text_input("Video Path")
    timestamps = c4.text_input("Timestamps")

    if st.button("Insert Data"):
        if match_id and teams and location and match_type and winner:
            try:
                insert_match_data(match_id, teams, location, match_type, winner, video_path, timestamps)
                st.success("Match data inserted successfully!")
            except Exception as e:
                st.error(f"Error inserting data: {e}, Try different Match ID.")
        else:
            st.error("Please fill out all required fields.")

st.navigation([MatchDataEntry],position='top').run()