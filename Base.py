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
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.io as pio
pio.templates.default = "plotly_dark"
import warnings
warnings.filterwarnings('ignore')

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

my_col = [
    '#0bb4ff',
    '#50e991',
    '#e6d800',
    '#9b19f5',
    '#ffa300'
]

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
                    timestamp_sec = frame_no / fps # Calculate timestamp in second
                    duration_sec = 1 / fps  # Duration of the frame in seconds

                    ## Save annotated frames class-wise
                    class_folder = os.path.join(output_frames_root, class_name)
                    os.makedirs(class_folder, exist_ok=True)

                    filename = os.path.join(
                        class_folder,
                        f"frame_{frame_no:06d}.jpg"
                    )
                    cv2.imwrite(filename, annotated_frame)

                    # Record detection details in results list
                    results_list.append({
                        "match_id": match_id,
                        "total_frames": total_frames,
                        "frame_no": frame_no,
                        "brand": class_name,
                        "time_sec": round(timestamp_sec, 2),
                        "duration_sec": round(duration_sec, 2),
                        "confidence": round(conf, 3),
                        "x1": int(x1), "y1": int(y1),
                        "x2": int(x2), "y2": int(y2),
                        "frame_path": filename,
                        "Created_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })

                    

        cap.release()

        # Save CSV
        df = pd.DataFrame(results_list)
        # Determine brand placement based on bounding box area
        def Placemet(df):
          Width = df['x2']-df['x1']
          Height = df['y2']-df['y1']
          df['Area'] = Width*Height
          df['brand_position'] = df['Area'].apply(lambda x: 'Jersey' if x < 5000 else(
                                                'Boundry' if (x > 5000) & (x < 10000) else(
                                                    'Ground' if (x > 10000) & (x < 50000) else(
                                                        'Overely'))))
          return df
        df = Placemet(df) 
        df = df[['match_id', 'total_frames', 'frame_no', 'brand', 'brand_position', 'time_sec', 'duration_sec', 'confidence', 'frame_path', 'Created_at']]
        df.to_csv(output_csv, index=False)
        df.to_sql(f"brands", engine, if_exists="append", index=False)

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
    "content": """ 
                You are an expert data analyst that converts user questions into a single, syntactically correct SQL query.
                Follow these rules:

                Only use the tables, columns, and relationships provided in the context.

                Do not invent new tables, columns, or joins.

                If the context is insufficient, respond exactly with: ‘INSUFFICIENT_CONTEXT’.

                Use {dialect} syntax and functions.

                Prefer simple, readable queries with clear aliases and proper indentation.

                Never run the query; only output the SQL.

                Do not include explanations, comments, or natural language in the output.

                Context (database schema and any relevant examples):
                {context}""" .format(
                        dialect=self.db.dialect, context=self.db.table_info
                    )}]
    messages.append({"role": "user", "content": user_input})
    sql_invoke = self.llm.invoke(messages)
    sql_query = str(sql_invoke.content).replace("```sql","")
    sql_query = str(sql_query).replace("```","")
    return sql_query
  
  def NL_Response(self,sql_query,db_result):
    message = [{"role":"system",
                "content": """
                You are a senior data analyst creating impressive, executive-ready summaries from SQL query results.  

                **MANDATORY FORMAT** (use emojis, bold headings, bullets only):  
                📊 **Key Insights** (1 sentence overview)  
                🔥 **Top Highlights** (3-5 bullets with emojis)  
                📈 **Trends & Patterns** (2-3 sentences on movements/correlations)  
                💡 **Actionable Recommendations** (3 bullets with next steps)  

                SQL Query: {query}  
                Results: {results} 

                Keep concise, use data-driven numbers, add business context. No fluff.
                """.format(query=sql_query,results=db_result)}]
    message.append({"role":"user","content":"Give the summary in markdown code "})
    response = self.llm.invoke(message)
    response = response.content
    return response

class visual_charts:
  def __init__(self):
    pass

  # KPIs
  def total_frames(self,df):
    return df['total_frames'].max()

  def total_time(self,df):
    return df['time_sec'].max()

  def total_brands(self,df):
    return len(df['brand'].unique())

  def total_placement(self,df):
    return len(df['brand_position'].unique())

  def brand_count(self,df):
    t_df = df['brand'].value_counts().reset_index()
    fig = px.bar(
        data_frame=t_df,
        x = 'brand',
        y = 'count',
        title='Brand Apperance frame count',
        color = 'count',
        color_continuous_scale=my_col
    )

    fig.update_layout(
              title ={'x':0.25},
          )
    fig.update_coloraxes(showscale=False)

    return fig

  def placement_count(self,df):
    t_df = df['brand_position'].value_counts().reset_index()
    fig = px.bar(
        data_frame=t_df,
        x = 'count',
        y = 'brand_position',
        color= 'count',
        title='Brand Position frame counts',
        color_continuous_scale=my_col
    )

    fig.update_layout(
              title ={'x':0.25},
              showlegend = False,
          )
    fig.update_coloraxes(showscale=False)

    return fig

  def dis_frame_count(self,df):
    fig = px.imshow(df.pivot_table(index='brand', columns='brand_position', values='time_sec',aggfunc='count'),
                    text_auto=True,
                    title = "Brand and its Placement frame count")
    fig.update_layout(
              title ={'x':0.5},
              showlegend = False,
              xaxis = dict(side='top',showgrid=False),
              yaxis = dict(showgrid=False)
          )
    fig.update_coloraxes(showscale=False)
    return fig

  def frame_trend(self,df):
    t_df = df['frame_no'].value_counts().sort_index().reset_index()
    fig = px.area(
        data_frame=t_df,
        x='frame_no',
        y = 'count',
        title='Brand Detection trent over Frame',
        color_discrete_sequence=my_col
    )
    fig.update_layout(
                  title ={'x':0.5},
                  showlegend = False,
                  xaxis = dict(showgrid=False,rangeslider=dict(visible=True)),
                  yaxis = dict(showgrid=True)
    )
    fig.update_coloraxes(showscale=False)

    return fig

  def brand_confidence(self,df):
    t_df = df.groupby('brand')['confidence'].mean().reset_index()
    t_df['confidence'] = round(t_df['confidence']*100,2)
    fig =  px.bar(data_frame=t_df,
                  x = 'confidence',
                  y = 'brand',
                  color = 'confidence',
                  color_continuous_scale=my_col)
    fig.update_layout(
                  title ={'x':0.25},
                  showlegend = False,
              )
    fig.update_coloraxes(showscale=False)

    return fig

  def brand_detection_time(self,df):
    t_df = df.groupby('brand')['duration_sec'].sum().reset_index()
    fig = px.bar(data_frame=t_df,
                x='brand',
                y='duration_sec',
                color='duration_sec',
                color_continuous_scale=my_col,
                title = 'Brand Detection Time',)
    fig.update_layout(
                  title ={'x':0.25},
                  showlegend = False,
              )
    fig.update_coloraxes(showscale=False)

    return fig

  def brand_time_dist(self,df):

      fig = px.imshow(df.pivot_table(index='brand', columns='brand_position', values='duration_sec',aggfunc='sum'),
                      text_auto=True,
                      title = "Brand and its Placement apperance duration in seconds")
      fig.update_layout(
                title ={'x':0.5},
                showlegend = False,
                xaxis = dict(side='top',showgrid=False),
                yaxis = dict(showgrid=False)
            )
      fig.update_coloraxes(showscale=False)

      return fig