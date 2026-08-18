import streamlit as st
from utils.db_functions import init_db, verify_user, register_user, verify_recovery_word, reset_password

# 1. Page Configuration
st.set_page_config(page_title="AI Study Planner", page_icon="📚", layout="centered")

# --- CSS TO HIDE SIDEBAR ON LOGIN ---
hide_sidebar_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    footer {visibility: hidden;}
    </style>
"""

init_db()

# Initialize Session States
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

def login():
    # Inject the CSS to hide the sidebar and default footer
    st.markdown(hide_sidebar_style, unsafe_allow_html=True)
    
    # --- BRANDING SECTION ---
    col1, col2 = st.columns([1, 4])
    with col1:
        # Make sure you have your logo in the assets folder!
        try:
            st.image("assets/logo.jpg", width=100)
        except:
            st.image("https://illustrations.popsy.co/gray/student-with-books.svg", width=120)
            
    with col2:
        st.title("AI Smart Study Planner")
        st.markdown("*Your personalized roadmap to academic excellence.*")
    
    tab1, tab2, tab3 = st.tabs(["🔑 Login", "📝 Sign Up", "🆘 Forgot Password"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username").strip()
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", type="primary", use_container_width=True)
            
            if submit:
                if verify_user(username, password):
                    st.session_state["logged_in"] = True
                    st.session_state["username"] = username
                    st.switch_page("pages/1_📊_Dashboard.py")
                else:
                    st.error("Invalid Username or Password. Please try again.")

    with tab2:
        st.info("Join thousands of students optimizing their study habits.")
        with st.form("register_form"):
            new_username = st.text_input("Choose a Username").strip()
            new_password = st.text_input("Choose a Password", type="password")
            recovery_word = st.text_input("Secret Recovery Word (e.g., Mother's Maiden Name)").strip()
            
            if st.form_submit_button("Create Account", use_container_width=True):
                if new_username and new_password and recovery_word:
                    if register_user(new_username, new_password, recovery_word):
                        st.success("✅ Account created! You can now log in.")
                    else:
                        st.error("⚠️ Username already exists.")
                else:
                    st.warning("Please fill in all fields.")

    with tab3:
        st.info("Answer your security question to reset your password.")
        with st.form("forgot_password_form"):
            recover_user = st.text_input("Username").strip()
            recover_word = st.text_input("Secret Recovery Word").strip()
            new_pass = st.text_input("Enter NEW Password", type="password")
            
            if st.form_submit_button("Reset Password", use_container_width=True):
                if recover_user and recover_word and new_pass:
                    if verify_recovery_word(recover_user, recover_word):
                        reset_password(recover_user, new_pass)
                        st.success("✅ Password reset! Please use the Login tab.")
                    else:
                        st.error("❌ Credentials incorrect.")
                else:
                    st.warning("Please fill in all fields.")
    
    st.markdown("---")
    st.caption("© 2026 AI Smart Study Planner | Optimized for Academic Success")

def landing_page():
    st.title("🚀 You are logged in!")
    st.write(f"Welcome back, **{st.session_state['username']}**.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Go to My Dashboard", type="primary", use_container_width=True):
            st.switch_page("pages/1_📊_Dashboard.py")
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state["logged_in"] = False
            st.session_state["username"] = ""
            st.rerun()

# --- MAIN LOGIC ---
if not st.session_state["logged_in"]:
    login()
else:
    landing_page()