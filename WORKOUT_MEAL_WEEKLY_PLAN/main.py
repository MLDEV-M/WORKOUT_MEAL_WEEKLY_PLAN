
#python -m pip install --upgrade pip --user
#pip install streamlit --user
#pip install supabase --user 
#python -m streamlit run main.py
# main.py
import streamlit as st
from pages import Authentication, TrackTodayExercises  # Import your custom modules

# Ensure the sidebar content is customized and only shows what we want
st.markdown(
    """<style>
        /* Hide default Streamlit sidebar page navigation (like "Main Page", "Def Auth", etc.) */
        [data-testid="stSidebarNav"] { display: none; }
    </style>""", 
    unsafe_allow_html=True
)

# Sidebar: Show custom content
with st.sidebar:
    if "is_authenticated" in st.session_state and st.session_state.is_authenticated:
        # Show user info and logout if authenticated
        st.subheader(f"👤 Logged in as {st.session_state.user['username']}")
        if st.button("Logout"):
            # Implement your logout logic here
            st.session_state.is_authenticated = False
            st.session_state.user = None
            st.success("Logged out successfully!")
    else:
        # Show login or signup if not authenticated
        st.subheader("🔑 Authentication")
        Authentication.display_auth_page()

# Main content: Only show track_today_exercises if logged in
if st.session_state.is_authenticated:
    TrackTodayExercises.display_track_exercises_page(st)
else:
    # Ensure the login screen is shown as the main page for unauthenticated users
    st.write("Please log in to access the app.")  # You can also show a login form directly if needed.
