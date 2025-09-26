from functions import extract_ai_contents
import streamlit as st
from auth import login_user, register_user, hash_password
from specialty import PROFESSION_SPECIALTIES
from database import init_db
from agents.news_agent import create_news_agent
from agents.chat_agent import create_chat_agent
from functions import display_results, extract_ai_contents
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
if "newsletter_results" not in st.session_state:
    st.session_state.newsletter_results = None

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
        
        # Add debug toggle to sidebar
        debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=False)
        
        if st.button("Get Today's Updates"):
            with st.spinner("Fetching relevant news..."):
                query = f"Latest healthcare news relevant for {user['profession']}"
                if user.get('specialty'):
                    query += f" specializing in {user['specialty']}"
                try:
                    result = st.session_state.news_agent.invoke({"messages": query})
                    st.session_state.newsletter_results = result # Store results in session state

                    # Debug output if enabled
                    if debug_mode:
                        st.sidebar.subheader("Debug Information")
                        st.sidebar.json(result, expanded=False)
                    
                    if st.session_state.newsletter_results:
                        content = extract_ai_contents(st.session_state.newsletter_results)
                        display_results(content)
                    
                    # Show raw output in debug mode
                    if debug_mode:
                        with st.expander("Raw Output"):
                            st.text(content)
                            
                except ValueError as e:
                    st.error(f"Agent error: {e}")
                    if debug_mode:
                        st.exception(e)  # Show full traceback
                except Exception as e:
                    st.error(f"Unexpected error: {e}")
                    if debug_mode:
                        st.exception(e)  # Show full traceback
    
    with tab2:
        st.header("Discuss News & Implications")

        # Initialize messages and thread_id for memory
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {"role": "assistant", "content": "Hello! I'm PULSE, your healthcare AI assistant. How can I help you today?"}
            ]
        
        # Create a unique thread_id for this user's conversation
        if "chat_thread_id" not in st.session_state:
            st.session_state.chat_thread_id = f"user_{user['email']}_chat"

        # --- Handle new input AFTER displaying messages ---
        # Display all messages first
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Now place chat input LAST so it stays at bottom
        if prompt := st.chat_input("Ask about healthcare news or its implications"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Generate AI response
            with st.spinner("Thinking..."):
                # For LangGraph agents with memory, we need to use invoke with thread_id
                response = st.session_state.chat_agent.invoke(
                    {"messages": [("user", prompt)]},
                    config={"configurable": {"thread_id": st.session_state.chat_thread_id}}
                )
                
                # Extract the AI response from the agent output
                if isinstance(response, dict) and "messages" in response:
                    # Get the last AI message from the response
                    ai_messages = [msg for msg in response["messages"] 
                                 if hasattr(msg, 'content') and msg.content and 
                                 hasattr(msg, '__class__') and 'AI' in msg.__class__.__name__]
                    if ai_messages:
                        response = ai_messages[-1].content
                    else:
                        response = "I apologize, but I couldn't generate a response. Please try again."
                else:
                    response = str(response)

            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Rerun immediately to show new messages above input
            st.rerun()




# Show appropriate interface based on auth state
if st.session_state.user:
    show_main()
else:
    show_auth()
