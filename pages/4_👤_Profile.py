import streamlit as st
import sqlite3
from utils.db_functions import get_user_history, get_user_profile, update_user_profile, reset_password
from utils.ui import render_header, render_footer

# 1. Security Check
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Please log in from the main page to view your profile.")
    st.stop()

render_header()

username = st.session_state['username']
user_data = get_user_history(username)
profile_data = get_user_profile(username)

# Extract profile data safely
full_name = profile_data[0] if profile_data[0] else "Student"
institution = profile_data[1] if profile_data[1] else "Not Provided"
degree_major = profile_data[2] if profile_data[2] else "Not Provided"
current_semester = profile_data[3] if profile_data[3] else "Not Provided"
target_cgpa = profile_data[4] if profile_data[4] else 0.0

st.title("👤 User Profile & Settings")

# --- UI TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🎓 Academic ID", "⚙️ Edit Profile", "🔐 Security", "🗄️ Raw Data"])

# --- TAB 1: ACADEMIC ID CARD ---
with tab1:
    st.markdown("### Digital Student ID")
    colA, colB = st.columns([1, 2])
    
    with colA:
        # A placeholder avatar image based on username
        st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=" + username, width=150)
        st.caption(f"Account ID: `{username}`")
        
    with colB:
        st.markdown(f"**Name:** {full_name}")
        st.markdown(f"**Institution:** {institution}")
        st.markdown(f"**Program:** {degree_major}")
        st.markdown(f"**Current Semester:** {current_semester}")
        st.markdown(f"**Target Goal:** {target_cgpa} CGPA")

    st.divider()
    
    # Lifetime Stats
    st.subheader("📊 Lifetime Account Statistics")
    if user_data.empty:
        st.write("No study logs found.")
    else:
        total_logs = len(user_data)
        total_study_hours = user_data['study_hours'].sum()
        
        stat1, stat2 = st.columns(2)
        stat1.metric("Total Study Sessions Logged", total_logs)
        stat2.metric("Total Hours Studied", f"{total_study_hours:.1f} hrs")

# --- TAB 2: EDIT PROFILE FORM ---
with tab2:
    st.markdown("### Update Your Information")
    with st.form("update_profile_form"):
        new_name = st.text_input("Full Name", value=full_name if full_name != "Student" else "")
        new_uni = st.text_input("University / Institution", value=institution if institution != "Not Provided" else "")
        new_major = st.text_input("Degree & Major", value=degree_major if degree_major != "Not Provided" else "", placeholder="e.g., B.Tech CSE")
        
        col1, col2 = st.columns(2)
        with col1:
            semesters = ["Semester 1", "Semester 2", "Semester 3", "Semester 4", "Semester 5", "Semester 6", "Semester 7", "Semester 8", "Other"]
            default_index = semesters.index(current_semester) if current_semester in semesters else 0
            new_sem = st.selectbox("Current Semester", semesters, index=default_index)
        with col2:
            new_cgpa = st.number_input("Target CGPA / Percentage Goal", min_value=0.0, max_value=100.0, value=float(target_cgpa), step=0.1)
            
        submit_profile = st.form_submit_button("💾 Save Profile Settings")
        if submit_profile:
            update_user_profile(username, new_name, new_uni, new_major, new_sem, new_cgpa)
            st.success("✅ Profile updated successfully!")
            st.rerun()

# --- TAB 3: ACCOUNT SECURITY ---
with tab3:
    st.markdown("### 🔐 Security & Privacy")
    st.write("Manage your account credentials and data privacy settings.")
    
    # 1. Change Password Form
    with st.expander("Change Account Password"):
        with st.form("change_pass_form"):
            new_pass = st.text_input("Enter New Password", type="password")
            confirm_pass = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Update Password"):
                if new_pass == confirm_pass and len(new_pass) > 0:
                    reset_password(username, new_pass)
                    st.success("✅ Password updated successfully!")
                else:
                    st.error("⚠️ Passwords do not match or are empty.")
    
    # 2. Delete Account (Danger Zone)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.error("🚨 Danger Zone")
    st.write("Deleting your account will permanently erase all your study logs and profile data. This cannot be undone.")
    
    if st.button("🗑️ Delete My Account Permanently", type="primary"):
        # Connect directly to delete the user
        conn = sqlite3.connect('data/database.db')
        c = conn.cursor()
        c.execute('DELETE FROM users WHERE username=?', (username,))
        c.execute('DELETE FROM study_logs WHERE username=?', (username,))
        conn.commit()
        conn.close()
        
        # Log them out and refresh
        st.session_state["logged_in"] = False
        st.session_state["username"] = ""
        st.rerun()

# --- TAB 4: RAW DATA EXPORT ---
with tab4:
    st.subheader("🗄️ Your Database History")
    if not user_data.empty:
        display_df = user_data.drop(columns=['id', 'username']) 
        display_df = display_df.rename(columns={
            'log_date': 'Date', 'subject': 'Subject', 'predicted_marks': 'Predicted Marks',
            'study_hours': 'Study Hrs', 'sleep_hours': 'Sleep Hrs', 'attendance': 'Attendance %',
            'assignments': 'Assignments %', 'consistency': 'Days/Week', 'days_remaining': 'Days to Exam',
            'previous_marks': 'Past Marks'
        })
        display_df = display_df.sort_values(by='Date', ascending=False) 
        cols = display_df.columns.tolist()
        cols.insert(0, cols.pop(cols.index('Date')))
        display_df = display_df[cols]
        
        st.dataframe(display_df, use_container_width=True)
        
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(label="Download data as CSV", data=csv, file_name=f"{username}_study_history.csv", mime="text/csv")
    else:
        st.info("No data available to display or download.")

render_footer()