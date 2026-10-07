import streamlit as st
from pathlib import Path
import sqlite3

from sqlalchemy import create_engine

from langchain.agents import create_agent
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_groq import ChatGroq


# -----------------------------
# Streamlit Configuration
# -----------------------------

st.set_page_config(
    page_title="LangChain: Chat with SQL DB",
    page_icon="🤖"
)

st.title("LangChain: Chat with SQL DB")


# -----------------------------
# Database Options
# -----------------------------

LOCALDB = "USE_LOCALDB"
MYSQL = "USE_MYSQL"

radio_opt = [
    "Use SQLite 3 Database - Employee.db",
    "Connect to SQL Database"
]

selected_opt = st.sidebar.radio(
    "Choose the DB which you want to chat with",
    radio_opt
)


if radio_opt.index(selected_opt) == 1:

    db_url = MYSQL

    mysql_host = st.sidebar.text_input(
        "Provide MySQL Host"
    )

    mysql_user = st.sidebar.text_input(
        "Provide MySQL User"
    )

    mysql_password = st.sidebar.text_input(
        "Provide MySQL Password",
        type="password"
    )

    mysql_db = st.sidebar.text_input(
        "Provide MySQL Database Name"
    )

else:

    db_url = LOCALDB


# -----------------------------
# Groq API Key
# -----------------------------

api_key = st.sidebar.text_input(
    "Provide your Groq API Key",
    type="password"
)

if not api_key:
    st.warning("Please add your Groq API Key.")
    st.stop()


# -----------------------------
# LLM
# -----------------------------

llm = ChatGroq(
    api_key=api_key,
    model="openai/gpt-oss-120b",
    streaming=True
)


# -----------------------------
# Configure Database
# -----------------------------

@st.cache_resource(ttl="1h")
def configure_db(
    db_url,
    mysql_host=None,
    mysql_user=None,
    mysql_password=None,
    mysql_db=None
):

    if db_url == LOCALDB:

        db_path = (
            Path(__file__).parent / "Employee.db"
        ).absolute()

        print(f"SQLite DB Path: {db_path}")

        creator = lambda: sqlite3.connect(
            f"file:{db_path}?mode=ro",
            uri=True
        )

        return SQLDatabase(
            create_engine(
                "sqlite:///",
                creator=creator
            )
        )

    elif db_url == MYSQL:

        if not all([
            mysql_host,
            mysql_user,
            mysql_password,
            mysql_db
        ]):
            st.error(
                "Please provide all MySQL connection details."
            )
            st.stop()

        return SQLDatabase(
            create_engine(
                f"mysql+mysqlconnector://"
                f"{mysql_user}:{mysql_password}"
                f"@{mysql_host}/{mysql_db}"
            )
        )


# -----------------------------
# Create Database
# -----------------------------

if db_url == MYSQL:

    db = configure_db(
        db_url,
        mysql_host,
        mysql_user,
        mysql_password,
        mysql_db
    )

else:

    db = configure_db(db_url)


# -----------------------------
# SQL Toolkit
# -----------------------------

toolkit = SQLDatabaseToolkit(
    db=db,
    llm=llm
)

tools = toolkit.get_tools()


# -----------------------------
# Agent
# -----------------------------

agent = create_agent(
    model=llm,
    tools=tools
)


# -----------------------------
# Chat History
# -----------------------------

if (
    "messages" not in st.session_state
    or st.sidebar.button("Clear Chat History")
):

    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "How can I help you?"
        }
    ]


for msg in st.session_state.messages:

    st.chat_message(
        msg["role"]
    ).write(
        msg["content"]
    )


# -----------------------------
# User Input
# -----------------------------

user_query = st.chat_input(
    "Ask your question here"
)


if user_query:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_query
        }
    )

    st.chat_message(
        "user"
    ).write(user_query)


    with st.chat_message("assistant"):

        streamlit_callback = StreamlitCallbackHandler(
            st.container()
        )

        response = agent.invoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": user_query
                    }
                ]
            },
            config={
                "callbacks": [
                    streamlit_callback
                ]
            }
        )

        answer = response["messages"][-1].content

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        st.write(answer)