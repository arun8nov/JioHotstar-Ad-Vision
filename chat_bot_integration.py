from langchain_community.utilities import SQLDatabase
from dotenv import load_dotenv
import os
import mysql.connector
import ollama
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

def query_result(chat_query,query_result, model_name="llama3.2:latest"):
    messages = [
        {"role": "system", "content": f"You are a helpful assistant that translates database query results into simple natural language. Given previouse query from user : {chat_query}"},
        {"role": "user", "content": f"Translate this database query result into a clear explanation: {query_result}"}
    ]
    
    response = ollama.chat(model=model_name, messages=messages)
    return response.message.content