from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os
import mysql.connector
load_dotenv()

db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
db_name = "jiohotstar_ads"


def get_db():
    db_path = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    db = SQLDatabase.from_uri(db_path)
    return db