# home.py - Smart Study Planner Homepage
import streamlit as st
from auth import auth_screen
from dashboard import show_dashboard

def show_home_page():
    """Show home page - redirects to dashboard if logged in"""
    if st.session_state.get("logged_in", False):
        show_dashboard()
    else:
        auth_screen()

# For backward compatibility
# auth_screen ကို auth.py ကနေခေါ်သုံးမယ်