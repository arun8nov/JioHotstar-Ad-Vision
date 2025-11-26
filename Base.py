from turtle import st
import mysql.connector
import sqlalchemy
from dotenv import load_dotenv
import os
import pandas as pd
import streamlit as st
from langchain_community.utilities import SQLDatabase
import ollama
import cv2
from ultralytics import YOLO
from langchain_google_genai import ChatGoogleGenerativeAI
from google import genai

# Load environment variables
load_dotenv()

db_host = os.getenv("db_host")
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_port = os.getenv("db_port")
db_name = os.getenv("db_name")
api_key = os.getenv("api_key")

engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
model_path = r"D:\GIT\JioHotstar-Ad-Vision\models\Ad_track.pt"
model = YOLO(model_path)

class Database_Intergration:

    def __init__(self):
        pass


    # Database connection
    def get_connection(self):
        Conn =  mysql.connector.connect(
                host=db_host,
                user=db_user,
                password=db_password,
                port=int(db_port),
                database=db_name
            )
        return Conn

    def sql_engine(self):
        engine = sqlalchemy.create_engine(f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}")
        return engine

    # Insert match data function
    def insert_match_data(self,match_id, teams, location, match_type, winner, video_path, match_timestamp):
        conn = self.get_connection()
        cursor = conn.cursor()
        insert_query = """
            INSERT INTO matches (match_id, teams, location, match_type, winner, video_path, match_timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
        cursor.execute(insert_query, (match_id, teams, location, match_type, winner, video_path, match_timestamp))
        conn.commit()
        cursor.close()
        conn.close()

    def Query_a_Table(self,Q):
      df = pd.read_sql(Q,self.get_connection())
      return df


    def Query(self,Q):
      conn = self.get_connection()
      cursor = conn.cursor()
      cursor.execute(Q)
      rows = cursor.fetchall()
      cursor.close()
      conn.close()
      return rows

    def Database_Reset(self,password):
        if password != "Admin@123":
            return 0
        else:
            my_db = self.get_connection()
            cursor = my_db.cursor()
            cursor.execute("DROP DATABASE IF EXISTS jiohotstar_ads")
            cursor.execute("CREATE DATABASE IF NOT EXISTS jiohotstar_ads")
            cursor.execute("USE jiohotstar_ads")

            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()

            cursor.execute("USE jiohotstar_ads")

            create_table_query = """
            CREATE TABLE IF NOT EXISTS matches (
                match_id INT PRIMARY KEY,
                teams VARCHAR(255),
                location VARCHAR(255),
                match_type VARCHAR(100),
                winner VARCHAR(255),
                video_path VARCHAR(255) UNIQUE,
                match_timestamp DATETIME NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """

            cursor.execute(create_table_query)
            my_db.commit()

            print("Database and table have been reset and created successfully.")

            cursor.close()
            my_db.close()

            return 1


class Tracking:
    def __init__(self):
        pass

    def ad_tracking_and_classwise_extraction(self,match_id, video_path, folder_path):

        
        # Folder and file setup
        output_csv = video_path.replace(".mp4", "_ad_tracking_details.csv")
        output_frames_root = os.path.join(folder_path, "extracted_frames")
        os.makedirs(output_frames_root, exist_ok=True)

        # Open video file for processing
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        results_list = []
        frame_no = 0
        # Process video frames
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_no += 1

            # YOLO Tracking
            results = model.track(frame, verbose=False)
            boxes = results[0].boxes
            # If detections exist, process them
            if boxes is not None and len(boxes) > 0:
                annotated_frame = results[0].plot()

                for box in boxes:
                    cls_id = int(box.cls[0].item())
                    conf = float(box.conf[0].item())
                    x1, y1, x2, y2 = box.xyxy[0].tolist()

                    class_name = results[0].names[cls_id]
                    timestamp_sec = frame_no / fps

                    # Record detection details in results list
                    results_list.append({
                        "match_id": match_id,
                        "frame": frame_no,
                        "time_sec": round(timestamp_sec, 2),
                        "total_frames": total_frames,
                        "brand": class_name,
                        "confidence": round(conf, 3),
                        "x1": int(x1), "y1": int(y1),
                        "x2": int(x2), "y2": int(y2)
                    })

                    ## Save annotated frames class-wise
                    class_folder = os.path.join(output_frames_root, class_name)
                    os.makedirs(class_folder, exist_ok=True)

                    filename = os.path.join(
                        class_folder,
                        f"frame_{frame_no:06d}.jpg"
                    )
                    cv2.imwrite(filename, annotated_frame)

        cap.release()

        # Save CSV
        df = pd.DataFrame(results_list)
        df.to_csv(output_csv, index=False)
        df.to_sql("brand_detections", engine, if_exists="append", index=False)

        print("✔ Process Completed!")
        print(f"CSV Saved → {output_csv}")
        print(f"Frames Saved → {output_frames_root}")



class lang_chain_db:
  def __init__(self):
    pass

  def get_db(self):
      db_path = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
      db = SQLDatabase.from_uri(db_path)
      return db

  def query_result(self,chat_query,query_result, model_name="llama3.2:1b"):
      messages = [
          {"role": "system", "content": f"You are a helpful assistant that translates database query results into simple natural language. Given previouse query from user : {chat_query}"},
          {"role": "user", "content": f"Translate this database query result into a clear explanation: {query_result}"}
      ]

      response = ollama.chat(model=model_name, messages=messages)
      return response.message.content
  
class GenAi_Chat:
  def __init__(self):
    pass
  
  llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key)
  db = lang_chain_db().get_db()
    
  def sql_query_gen(self,user_input):
    messages = [{"role": "system", 
    "content": f"You are a sql query generator. Generate a sql query based on the user input. only return the sql query.Only single query output,without any explaination or any other text. Tabel info is given below: {self.db.get_table_info()}"}]
    messages.append({"role": "user", "content": user_input})
    sql_invoke = self.llm.invoke(messages)
    sql_query = str(sql_invoke.content).replace("```sql","")
    sql_query = str(sql_query).replace("```","")
    return sql_query
  
  def NL_Response(self,sql_query,db_result):
    message = [{"role":"system","content":f"You are an expert an analyse the data from database. You will given sql query {sql_query}, output of a sql quey. you have to analyse the data . The Output of the sql query: {db_result} "}]
    message.append({"role":"user","content":"Give 10 line summary in markdown code"})
    response = self.llm.invoke(message)
    response = response.content
    return response
