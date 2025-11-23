import os
from dotenv import load_dotenv
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_ollama import ChatOllama

load_dotenv()

try:
    # Database Connection
    db_user = os.getenv("db_user")
    db_password = os.getenv("db_password")
    db_host = os.getenv("db_host")
    db_port = os.getenv("db_port")
    db_name = "jiohotstar_ads"

    db_uri = f"mysql+mysqlconnector://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    db = SQLDatabase.from_uri(db_uri)
    print("Database connected successfully.")
    print(f"Dialect: {db.dialect}")
    print(f"Tables: {db.get_usable_table_names()}")

    # Initialize LLM
    llm = ChatOllama(model="llama3.2:latest", temperature=0)
    print("LLM initialized.")

    # Create SQL Agent
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    print("Agent created.")

    # Example Query
    print("Running query...")
    response = agent_executor.invoke("List the tables in the database")
    print(f"Response: {response}")

except Exception as e:
    print(f"Error: {e}")
