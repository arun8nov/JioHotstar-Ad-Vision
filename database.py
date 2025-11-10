import mysql.connector
from dotenv import load_dotenv
import os

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
def insert_match_data(match_id, teams, location, match_type, winner, video_path, timestamps):
    conn = get_connection()
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO matches (match_id, teams, location, match_type, winner, video_path, timestamps)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_query, (match_id, teams, location, match_type, winner, video_path, timestamps))
    conn.commit()
    cursor.close()
    conn.close()