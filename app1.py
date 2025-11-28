import streamlit as st
import os
import datetime
import time
from dotenv import load_dotenv

# Load predefined function using class and object methode
from Base import Database_Intergration,Tracking,lang_chain_db,GenAi_Chat,visual_charts

# Load environment variables
load_dotenv()


Db_I = Database_Intergration()
Track = Tracking()
LC_db = lang_chain_db()
GE = GenAi_Chat()
chart = visual_charts()


# Web page title & icon
st.set_page_config(page_title = "Ai-powerd Criket ads regonition",
                   page_icon = "🏏",layout = "wide")




# Match details Entry and Ad Tracking
def MatchDataEntry():
    st.image('"front_dark.png"')
    c1,c2 = st.columns([0.3,2])
    c1.image("ball_logo.png") # Seeting up Logo
    c2.title("Match Data Entry") # Seeting up Logo and Title
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
        st.info(f"Video will be saved to 'data\{match_id}\{video_file.name}'")



    if st.button("Insert Data & Add Tracking") and video_file is not None:
        if match_id and teams and location and match_type and winner and video_file :
            # Folter create directory if not exists
            folder_path = f"data\{match_id}"
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            video_path = f"data\{match_id}\source_video.mp4"

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
    match_df = Db_I.Query_a_Table("SELECT * FROM matches;")
    st.dataframe(match_df)
    st.subheader(f"Brand Detections of Match_{match_id}")
    try:
        brand_detections_df = Db_I.Query_a_Table(f"SELECT * FROM brands WHERE match_id = {match_id};")
        st.dataframe(brand_detections_df)
    except Exception as e:
        st.error(f"Once Add Tracking is run for Match ID {match_id}, the brand detections will be displayed here.The error is: {e}")

# Visual chart of ad trackers
def Add_Tracking_Visuals():
    c1,c2 = st.columns([0.3,2])
    c1.image("eye_logo.png") # Seeting up Logo
    c2.title("Add Tracking Visuals") # Seeting up Logo and Title
    match_id = st.number_input("Enter Match ID for Visuals", min_value=1, step=1)
    if st.button("Generate Visuals"):
        with st.spinner("Generating Visuals..."):
            try:
                df = Db_I.Query_a_Table(f"SELECT * FROM brands WHERE match_id = {match_id};")
                st.dataframe(df)
                total1,total2,total3,total4 = st.columns(4,gap='small')
                with total1:
                    st.info("Total Frames",icon='🎞️')
                    st.metric(label="Total frames formed in video",value=f"{chart.total_frames(df)}",border=True,)
                with total2:
                    st.info("Total Time",icon='🕒')
                    st.metric(label="Total video time in seconds",value=f"{chart.total_time(df)}",border=True,)
                with total3:
                    st.info("Total Brands",icon='🏷️')
                    st.metric(label="Total brands detected",value=f"{chart.total_brands(df)}",border=True,)
                with total4:
                    st.info("Total Placements",icon='🎯')
                    st.metric(label="Total placements of brands detected",value=f"{chart.total_placement(df)}",border=True,)

                c1,c2,c3 = st.columns(3)
                c1.plotly_chart(chart.brand_count(df))
                c2.plotly_chart(chart.placement_count(df))
                c3.plotly_chart(chart.dis_frame_count(df))

                c1,c2 = st.columns([3,2])
                c1.plotly_chart(chart.frame_trend(df))
                c2.plotly_chart(chart.brand_confidence(df))

                c1,c2 = st.columns(2)
                c1.plotly_chart(chart.brand_detection_time(df))
                c2.plotly_chart(chart.brand_time_dist(df))

                st.plotly_chart(chart.brand_distribution_over_time(df))

            except Exception as e:
                st.error(f"Error fetching brand data: {e}")

# Ai powerd SQL Rag
def chat_interface():
    c1,c2 = st.columns([0.3,2])
    c1.image("chat_logo.png") # Seeting up Logo
    c2.title("Chat Interface") # Seeting up Logo and Title
    db = LC_db.get_db()
    tables_names = db.get_table_names()
    st.title("Database Overview")
    st.info(f"Databases Tables: {', '.join(tables_names)}")
    c1,c2=st.columns(2)
    c1.subheader(f"{tables_names[0]} table Sample Data")
    sql_query = Db_I.Query_a_Table(f"SELECT * FROM {tables_names[0]} LIMIT 1;")
    c1.dataframe(sql_query)
    try:
        c2.subheader(f"{tables_names[1]} table Sample Data")
        sql_query = Db_I.Query_a_Table(f"SELECT * FROM {tables_names[1]} LIMIT 1;")
        c2.dataframe(sql_query)
    except:
        c2.info("Only one table in database")

    # Chat Interface
    st.title("Ai powered SQL Chatbot")
    st.info("Ask questions about the database and get answers with SQL queries and results.")
    # User chatbox
    user_input = st.chat_input("Ask a question about the database")
    if user_input:
        with st.spinner("Generating SQL query..."):
            # LLM Querying
            sql_query = GE.sql_query_gen(user_input)
            st.write(sql_query)
            print(sql_query)
            result_from_database = Db_I.Query_a_Table(sql_query)
            st.dataframe(result_from_database)
            # LLM Ans
            ans = GE.NL_Response(sql_query,result_from_database)
            st.markdown(f""" {ans} """)

# Admin control
def Admin_Interface():
    st.title("Admin Interface")

    password = st.text_input("Admin Password", type="password")
    if st.button("Reset Database"): # Database reset
        with st.spinner("Resetting database..."):
            if password:
                DBR =Db_I.Database_Reset(password)
                if DBR == 0:
                    st.error("Incorrect password. Database reset aborted.")
                else:
                    st.success("Database has been reset.")
                    st.info("You can now re-enter match data.")


st.navigation([MatchDataEntry,Add_Tracking_Visuals,chat_interface,Admin_Interface],position='top').run()
