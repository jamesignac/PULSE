import streamlit as st
from auth import login_user, register_user, hash_password
from specialty import PROFESSION_SPECIALTIES
from database import init_db
from agents.news_agent import create_news_agent
from agents.chat_agent import create_chat_agent
from dotenv import load_dotenv
import os
import sqlite3
import os.path
from pathlib import Path
import json

# Initialize database
init_db()

load_dotenv('.env')


# App title
st.title("PULSE: Personalized Updates & Learning System for Experts")

# Session state initialization
if 'user' not in st.session_state:
    st.session_state.user = None
if 'news_agent' not in st.session_state:
    st.session_state.news_agent = None
if 'chat_agent' not in st.session_state:
    st.session_state.chat_agent = None
if 'profession' not in st.session_state:
    st.session_state.profession = None
if 'specialty' not in st.session_state:
    st.session_state.specialty = None

# Authentication
def show_auth():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if login_user(email, password):
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    
    with tab2:
        # Profession and specialty selection OUTSIDE the form for dynamic update
        profession = st.selectbox(
            "Profession",
            list(PROFESSION_SPECIALTIES.keys()),
            key="profession_select_dynamic"
        )
        specialty = st.selectbox(
            "Specialty",
            PROFESSION_SPECIALTIES[profession],
            key="specialty_select_dynamic"
        )
        with st.form("register_form"):
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            # Use profession and specialty selected above
            st.write(f"Profession: {profession}")
            st.write(f"Specialty: {specialty}")
            submitted = st.form_submit_button("Register")
            if submitted:
                if password != confirm_password:
                    st.error("Passwords don't match")
                elif not first_name or not last_name:
                    st.error("Please enter your first and last name.")
                else:
                    try:
                        register_user(email, password, profession, specialty, first_name, last_name)
                        st.success("Registration successful! Please login.")
                    except ValueError as e:
                        st.error(str(e))

# Main app
def show_main():
    user = st.session_state.user
    sidebar_greeting = f"Welcome, {user['first_name']}!" if user.get('first_name') else f"Welcome, {user['profession']}"
    st.sidebar.title(sidebar_greeting)
    if user.get('specialty'):
        st.sidebar.write(f"Specialty: {user['specialty']}")
    
    # Initialize agents if not already done
    if not st.session_state.news_agent:
        st.session_state.news_agent = create_news_agent(
            user['profession'], 
            user.get('specialty')
        )
    
    if not st.session_state.chat_agent:
        st.session_state.chat_agent = create_chat_agent(
            user['profession'], 
            user.get('specialty')
        )
    
    # App tabs
    tab1, tab2 = st.tabs(["Daily Newsletter", "Chat with AI"])
    
    with tab1:
        st.header("Your Personalized Healthcare News")
        if st.button("Get Today's Updates"):
            with st.spinner("Fetching relevant news..."):
                query = f"Latest healthcare news relevant for {user['profession']}"
                if user.get('specialty'):
                    query += f" specializing in {user['specialty']}"
                try:
                    result = st.session_state.news_agent.invoke({"input": query})
                    if isinstance(result, dict) and 'output' in result:
                        st.markdown(result['output'])
                    else:
                        st.error("No news was returned.")
                except ValueError as e:
                    st.error(f"Agent error: {e}")
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
    
    with tab2:
        st.header("Discuss News & Implications")
        
        # Initialize messages if not exists
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Initialize with a welcome message
            welcome_msg = f"Hello! I'm your healthcare AI assistant. How can I help you today?"
            st.session_state.messages.append({"role": "assistant", "content": welcome_msg})
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat input always at the bottom
        prompt = st.chat_input("Ask about healthcare news or its implications")
        if prompt:
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)

            # Generate AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    # Get the conversation history in the correct format
                    history = "\n".join(
                        f"{msg['role']}: {msg['content']}"
                        for msg in st.session_state.messages[:-1]
                    )

                    # Get AI response
                    response = st.session_state.chat_agent.predict(
                        input=prompt,
                        history=history
                    )

                    st.markdown(response)

            # Add assistant response to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})

# Show appropriate interface based on auth state
if st.session_state.user:
    show_main()
else:
    show_auth()
