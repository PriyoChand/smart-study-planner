import streamlit as st
import pandas as pd
import pickle
import time
from datetime import date
from utils.db_functions import init_db, save_study_log
from utils.ui import render_header, render_footer

# 1. Security Check & UI
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Please log in from the main page to access this feature.")
    st.stop()

init_db()
render_header()

# 2. Load the AI Model
@st.cache_resource
def load_model():
    # Ensuring path is correct for your local structure
    with open('model/model/marks_predictor.pkl', 'rb') as file:
        return pickle.load(file)

model = load_model()

# --- THE CALLBACK FUNCTION (Processes data before page redraws) ---
def process_study_log():
    # 1. Access widget values via session_state keys
    sh = st.session_state.elapsed_hours
    slh = st.session_state.sleep_input
    att = st.session_state.attendance_input
    ass = st.session_state.assignments_input

    # 2. Validation Logic
    if (sh + slh) > 24.0:
        st.session_state.ui_message = {"type": "error", "content": "🚨 Logic Error: Combined Study and Sleep cannot exceed 24 hours!"}
        return
    elif sh == 0 and att == 0 and ass == 0:
        st.session_state.ui_message = {"type": "warning", "content": "⚠️ Form is blank. Please enter your study metrics before saving."}
        return

    # 3. Data Collection
    subj = st.session_state.subject_input
    con = st.session_state.consistency_input
    dr = st.session_state.days_remaining_input
    pm = st.session_state.prev_marks_input
    fs = st.session_state.focus_score_input
    sn = st.session_state.session_notes_input

    # 4. AI Prediction
    input_data = pd.DataFrame({
        'Subject': [subj], 'Study_Hours': [sh], 'Sleep_Hours': [slh],
        'Attendance_Pct': [att], 'Assignments_Completed': [ass],
        'Daily_Consistency': [con], 'Study_Days_Remaining': [dr],
        'Previous_Marks': [pm]
    })
    
    predicted_mark = round(model.predict(input_data)[0], 1)
    
    # ML Guardrails
    if sh <= 1.0 and att <= 20 and ass <= 20: 
        predicted_mark *= 0.2
    elif predicted_mark > 100: 
        predicted_mark = 100.0
    elif predicted_mark < 0: 
        predicted_mark = 0.0

    # 5. Database Save
    username = st.session_state["username"]
    today_date = date.today() 
    save_study_log(
        username, today_date, subj, sh, slh, att, ass, con, dr, pm, predicted_mark, fs, sn
    )

    # 6. Success State
    st.session_state.ui_message = {
        "type": "success", 
        "subj": subj, 
        "date": today_date, 
        "mark": predicted_mark
    }

    # 7. Reset Widgets (Safely resets the UI to 0)
    st.session_state.elapsed_hours = 0.0
    st.session_state.sleep_input = 0.0
    st.session_state.attendance_input = 0
    st.session_state.assignments_input = 0
    st.session_state.consistency_input = 0
    st.session_state.days_remaining_input = 0
    st.session_state.prev_marks_input = 0.0
    st.session_state.focus_score_input = 3
    st.session_state.session_notes_input = ""

# --- MAIN UI ---
st.title("📝 Log Daily Study Data")

# 🛡️ NULL-SAFE MESSAGE DISPLAY
if "ui_message" in st.session_state and st.session_state.ui_message is not None:
    msg = st.session_state.ui_message
    if msg.get("type") == "error":
        st.error(msg.get("content"))
    elif msg.get("type") == "warning":
        st.warning(msg.get("content"))
    elif msg.get("type") == "success":
        st.success(f"✅ Data saved for {msg.get('subj')} on {msg.get('date')}!")
        st.info(f"🤖 AI Prediction: **{msg.get('mark')}/100**")

# --- POMODORO SECTION ---
with st.expander("⏱️ Use Focus Timer", expanded=False):
    colA, colB = st.columns([1, 2])
    
    if "elapsed_hours" not in st.session_state:
        st.session_state.elapsed_hours = 0.0
        
    with colA:
        if st.button("▶️ Start 25m Session", use_container_width=True):
            placeholder = st.empty()
            # Set to 1500 for real 25 mins. Using 3 for quick testing.
            for i in range(1500, -1, -1):
                m, s = divmod(i, 60)
                placeholder.markdown(f"### ⏳ {m:02d}:{s:02d}")
                time.sleep(1)
            st.session_state.elapsed_hours += 0.5
            st.balloons()
            st.rerun()
    with colB:
        st.write("Timer results are automatically added to Study Hours below.")

st.divider()

# --- ENTRY FORM ---
with st.form("study_entry_form"):
    st.selectbox("Subject", ['Python Programming', 'DBMS', 'Data Analytics', 'Operating Systems', 'Algorithms'], key="subject_input")
    
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Study Hours", min_value=0.0, max_value=24.0, step=0.5, key="elapsed_hours")
        st.number_input("Sleep Hours", min_value=0.0, max_value=24.0, step=0.5, key="sleep_input")
        st.slider("Attendance %", 0, 100, key="attendance_input")
        st.slider("Assignments %", 0, 100, key="assignments_input")
    with c2:
        st.slider("Consistency (Days/Wk)", 0, 7, key="consistency_input")
        st.number_input("Days to Exam", min_value=0, max_value=365, key="days_remaining_input")
        st.number_input("Past Marks", min_value=0.0, max_value=100.0, key="prev_marks_input")
    
    st.divider()
    st.markdown("### 🧠 Session Qualitative Data")
    st.slider("Focus Score (1-5)", 1, 5, key="focus_score_input")
    st.text_area("Notes", placeholder="What did you learn or struggle with today?", key="session_notes_input")

    # on_click handles the logic before the refresh to prevent API errors
    st.form_submit_button("Predict & Save", type="primary", on_click=process_study_log)

render_footer()