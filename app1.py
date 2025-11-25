import streamlit as st
from dotenv import load_dotenv
import os
import datetime
import time
import ollama

from Base import Database_Intergration,Tracking,lang_chain_db

Db_I = Database_Intergration()
Track = Tracking()
LC_db = lang_chain_db()
GE = GenAi_Chat()



st.set_page_config(page_title = "joihotstar Ads",
                   page_icon = "Jio",layout = "wide")

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



    if st.button("Insert Data") and video_file is not None:
        if match_id and teams and location and match_type and winner and video_file :
            # Folter create directory if not exists
            folder_path = rf"data/{match_id}"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            video_path = f"data/{match_id}/source_video.mp4"

            try:
                # Insert data into the database
                Db_I.insert_match_data(match_id, teams, location, match_type, winner, video_path, match_timestamp)

                # Save the uploaded video file
                with open(video_path, "wb") as f:
                    f.write(video_file.getbuffer())
                st.success("Match data inserted successfully! and video saved.")
                # Display the uploaded video
                st.video(video_file)
                # Run Ad Tracking
                with st.spinner("Running Ad Tracking..."):
                    Track.ad_tracking_and_classwise_extraction(match_id,video_path,folder_path)
                st.success("Ad Tracking completed and results saved.")


            except Exception as e:
                st.error(f"Error inserting data: {e}")
        else:
            st.error("Please fill out all required fields.")

    st.subheader("Current Tables in Database")
    tables = Db_I.Query("SHOW TABLES;")
    st.text(','.join([table[0] for table in tables]))
    st.subheader("Matches Table Data")
    df = Db_I.Query_a_Table("SELECT * FROM matches;")
    st.dataframe(df)

def chat_interface():
    model_name = "llama3.2:1b"  # replace with your actual model name
    db = LC_db.get_db()

    st.info("Databases Tables:")
    tables_names = db.get_table_names()
    st.table(tables_names,border='horizontal')

    user_input = st.chat_input("Ask a question about the database")
    if user_input:
        with st.spinner("Generating SQL query..."):
            sql_query = GE.sql_query_gen(user_input)
            st.write(sql_query)
            print(sql_query)
            result_from_database = Db_I.Query_a_Table(sql_query)
            st.dataframe(result_from_database)
            ans = GE.NL_Response(sql_query,result_from_database)
            st.markdown(ans)

st.navigation([MatchDataEntry,chat_interface],position='top').run()



