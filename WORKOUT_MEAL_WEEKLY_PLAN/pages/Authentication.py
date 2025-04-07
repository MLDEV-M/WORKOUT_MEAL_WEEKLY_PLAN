def display_auth_page():  
    import streamlit as st
    from supabase import create_client, Client
    import time

    SUPABASE_URL = st.secrets["supabase"]["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["supabase"]["SUPABASE_KEY"]

    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    # Initialize session state variables
    if "user" not in st.session_state:
        st.session_state.user = None
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False  # Store auth status

    def login():
        st.subheader("🔑 Login with Username")
        username = st.text_input("👤 Username", key="login_username")
        password = st.text_input("🔒 Password", type="password", key="login_password")

        if st.button("Login"):
            try:
                response = supabase.table("users").select("*").eq("username", username).execute()
                user_data = response.data

                if user_data and user_data[0]["password"] == password:
                    st.session_state.user = user_data[0]  # Store user session
                    st.session_state.is_authenticated = True  # Set auth flag
                    st.success(f"✅ Welcome, {username}!")
                    time.sleep(1)
                    st.rerun()  # Refresh UI
                else:
                    st.error("❌ Invalid username or password.")
            except Exception as e:
                st.error(f"❌ Login error: {e}")

    def signup():
        st.subheader("📝 Create a New Account")
        username = st.text_input("👤 Choose a Username", key="signup_username")
        password = st.text_input("🔒 Choose a Password", type="password", key="signup_password")

        if st.button("Sign Up"):
            try:
                existing_user = supabase.table("users").select("*").eq("username", username).execute()
                if existing_user.data:
                    st.error("⚠️ Username already taken. Try another one.")
                    return

                supabase.table("users").insert({"username": username, "password": password}).execute()
                st.success("✅ Account created! Please log in.")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"❌ Signup failed: {e}")

    def logout():
        st.session_state.user = None
        st.session_state.is_authenticated = False  # Reset auth flag
        st.success("🚪 Logged out successfully!")
        time.sleep(1)
        st.rerun()

    
    # Authentication handling
    if st.session_state.is_authenticated:
        st.subheader(f"👤 Logged in as {st.session_state.user['username']}")
        if st.button("Logout"):
            logout()
    else:
        st.subheader("🔑 Login or Sign Up")
        login()
        st.write("--- OR ---")
        signup()

    return st.session_state.is_authenticated  # Return authentication status

