from polars import sql
import streamlit as st
from dotenv import load_dotenv
import os
import datetime
import time
import ollama
from database import insert_match_data,Query,Query_a_Table
from track import Tracking
from chat_bot_integration import get_db,query_result

Track = Tracking()

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
                insert_match_data(match_id, teams, location, match_type, winner, video_path, match_timestamp)
                
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
    tables = Query("SHOW TABLES;")
    st.text(','.join([table[0] for table in tables]))
    st.subheader("Matches Table Data")
    df = Query_a_Table("SELECT * FROM matches;")
    st.dataframe(df)

def chat_interface():
    model_name = "llama3.2:latest"  # replace with your actual model name
    db = get_db()   

    st.info("Databases Tables:")
    tables_names = db.get_table_names()
    st.table(tables_names,border='horizontal')
    
    messages = [{"role": "system", 
    "content": f"You are a sql query generator. Generate a sql query based on the user input. only return the sql query.Only single query output,without any explaination or any other text. Tabel info is given below: {db.get_table_info()}"}]
    user_input = st.chat_input("Ask a question about the database")
    if user_input:
        with st.spinner("Generating SQL query..."):
            messages.append({"role": "user", "content": user_input})
            response = ollama.chat(model=model_name, messages=messages)
            sql_query = response.message.content
            st.write(sql_query)
            sql_query = sql_query.replace('```sql',' ').replace('```','').strip()
            print(sql_query)
            result = Query_a_Table(sql_query)
            st.dataframe(result)
            ans = query_result(chat_query=user_input,query_result=result)
            st.markdown(ans)

st.navigation([MatchDataEntry,chat_interface],position='top').run()




