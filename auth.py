import streamlit as st
import hashlib
from database import get_user, add_user

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def login_user(email: str, password: str) -> bool:
    user = get_user(email)
    if user and user['password'] == hash_password(password):
        st.session_state['user'] = user
        return True
    return False

def register_user(email: str, password: str, profession: str, specialty: str = None, first_name: str = None, last_name: str = None):
    # Accepts first_name and last_name as additional arguments
    import inspect
    frame = inspect.currentframe()
    args, _, _, values = inspect.getargvalues(frame)
    first_name = values.get('first_name')
    last_name = values.get('last_name')
    if get_user(email):
        raise ValueError("Email already registered")
    hashed_password = hash_password(password)
    if first_name is None or last_name is None:
        raise ValueError("First and last name are required.")
    add_user(email, hashed_password, first_name, last_name, profession, specialty)