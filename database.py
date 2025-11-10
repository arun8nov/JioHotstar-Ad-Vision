import mysql.connector
from dotenv import load_dotenv
import os
import pandas as pd

# Load environment variables
load_dotenv()

# Database connection
def get_connection():
    Conn =  mysql.connector.connect(
            host=os.getenv("db_host"),
            user=os.getenv("db_user"),
            password=os.getenv("db_password"),
            port=int(os.getenv("db_port")),
            database="jiohotstar_ads"
        )
    return Conn

# Insert match data function
def insert_match_data(match_id, teams, location, match_type, winner, video_path, match_timestamp):
    conn = get_connection()
    cursor = conn.cursor()
    insert_query = """
        INSERT INTO matches (match_id, teams, location, match_type, winner, video_path, match_timestamp)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
    cursor.execute(insert_query, (match_id, teams, location, match_type, winner, video_path, match_timestamp))
    conn.commit()
    cursor.close()
    conn.close()

def Query_a_Table(Q):
    df = pd.read_sql(Q,get_connection())
    return df

def Query(Q):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(Q)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows