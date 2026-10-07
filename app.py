import streamlit as st
import pathlib as Path
from langchain.agents import create_sql_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq

st.set_page_config(page_title="Langchain: Chat with SQL DB", page_icon=":robot:")
st.title("Langchain: Chat with SQL DB")

LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_opt=["Use SQLite 3 Database - Employee.db", "Connect to SQL Database"]

selected_opt=st.sidebar.radio("Choose the db which you want to chat with", radio_opt)

if radio_opt.index(selected_opt) == 1:
    db_url=MYSQL
    mysql_host=st.sidebar.text_input("Provide MySQL Host")
    mysql_user=st.sidebar.text_input("Provide MySQL User")
    mysql_password=st.sidebar.text_input("Provide MySQL Password", type="password")
    mysql_db=st.sidebar.text_input("Provide MySQL Database Name")
else:
    db_url=LOCALDB
    
api_key=st.sidebar.text_input("Provide your Groq API Key", type="password")

if not db_url:
    st.info("Please enter the database information and url.")
    
if not api_key:
    st.info("Please add your Groq API Key.")
    
## LLM Model
llm=ChatGroq(groq_api_key=api_key, model="openai/gpt-oss-120b", streaming=True)

@st.cache_resource(ttl="1h")
def configure_db(db_url,mysql_host=None, mysql_user=None, mysql_password=None, mysql_db=None):
    if db_url==LOCALDB:
        db_path=(Path.Path(__file__).parent / "Employee.db").absolute()
        print(f"SQLite DB Path: {db_path}")
        creator=lambda: sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    elif db_url==MYSQL:
        if not all([mysql_host, mysql_user, mysql_password, mysql_db]):
            st.error("Please provide all MySQL connection details.")
            st.stop()        
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))
  
if db_url==MYSQL:
    db=configure_db(db_url, mysql_host, mysql_user, mysql_password, mysql_db)
else:
    db=configure_db(db_url)
    
## Toolkit
