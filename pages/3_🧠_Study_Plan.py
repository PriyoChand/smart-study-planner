import streamlit as st
import pandas as pd
from utils.db_functions import get_user_history, get_user_profile
from utils.ui import render_header, render_footer

# 1. Access Control
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Please log in to view your personalized study plan.")
    st.stop()

render_header()

# 2. Fetch Data
username = st.session_state['username']
df = get_user_history(username)
profile = get_user_profile(username)
display_name = profile[0] if profile and profile[0] else username

st.title("📅 AI Study Planner")
st.markdown(f"Hey **{display_name}**, let's optimize your schedule based on your AI performance data.")

# --- SCENARIO: NO DATA ---
if df.empty:
    st.info("💡 I need some data to build a plan for you! Log a study session first.")
    if st.button("Go to Log Study"):
        st.switch_page("pages/2_📝_Log_Study.py")
    st.stop()

# --- AI RECOMMENDATION ENGINE ---
# Group data for ALL subjects
subject_stats = df.groupby('subject').agg({
    'predicted_marks': 'mean',
    'study_hours': 'sum'
}).reset_index()

# Find the "Critical" subject (lowest mark) for the Mission logic
weak_subject_row = subject_stats.loc[subject_stats['predicted_marks'].idxmin()]
weak_subject = weak_subject_row['subject']
weak_mark = round(weak_subject_row['predicted_marks'], 1)

# Find the "Neglected" subject (least hours)
neglected_subject = subject_stats.loc[subject_stats['study_hours'].idxmin(), 'subject']

st.divider()

# --- NEW SECTION: SUBJECT STATUS REPORT (Shows All Subjects) ---
st.subheader("📚 Subject Status Report")
st.markdown("Overview of your current standing across all subjects.")

# This creates a row of metrics for every subject found in your data
num_subjects = len(subject_stats)
cols = st.columns(num_subjects)

for i, (index, row) in enumerate(subject_stats.iterrows()):
    with cols[i]:
        s_name = row['subject']
        s_mark = round(row['predicted_marks'], 1)
        
        # UI logic for colors
        if s_mark < 50:
            status_label = "🔴 Critical"
            d_color = "inverse"
        elif s_mark < 80:
            status_label = "🟡 Improving"
            d_color = "normal"
        else:
            status_label = "🟢 Excellent"
            d_color = "normal"
            
        st.metric(label=s_name, value=f"{s_mark}%", delta=status_label, delta_color=d_color)

st.divider()

# --- SECTION 1: TODAY'S MISSION (The AI Priority) ---
st.subheader("🚀 Today's AI Mission")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown(f"### Priority: **{weak_subject}**")
    st.write(f"Your overall prediction is lowest in **{weak_subject}**. Strengthening this area will provide the biggest boost to your Semester Wave.")
    
    # Dynamic Advice
    if weak_mark < 40:
        st.error("🚨 **Urgent Action Required:** You are at risk of failing this subject. Focus on fundamentals today.")
    elif weak_mark < 75:
        st.warning("⚠️ **Boost Needed:** Focus on previous exam papers to push this score above 80%.")
    else:
        st.success("✨ **Maintenance:** You're doing well! Just a quick 30-min review will keep you on top.")

with col2:
    st.metric("Focus Subject", f"{weak_mark}%", "Priority #1", delta_color="inverse")

st.divider()

# --- SECTION 2: THE SEMESTER STRATEGY ---
st.subheader("🎯 Semester Strategy")

t1, t2 = st.tabs(["Time Balance", "Action Steps"])

with t1:
    if weak_subject == neglected_subject:
        st.write(f"🤖 **AI Insight:** It's clear why marks are low in **{weak_subject}**. You've spent the least amount of time on it. Increasing effort here will move your 'Semester Wave' up the fastest.")
    else:
        st.write(f"🤖 **AI Insight:** You are studying **{weak_subject}**, but the quality of focus might be low. Try using the Pomodoro timer on the Log page.")

with t2:
    st.markdown(f"""
    1. ⏱️ **Block 2 Hours:** Dedicate your next session exclusively to **{weak_subject}**.
    2. 🧠 **Focus Max:** Aim for a Focus Score of 5/5.
    3. 😴 **Recovery:** Ensure you get at least 7 hours of sleep tonight to lock in what you learn.
    """)

# --- SECTION 3: QUICK TODO LIST ---
st.divider()
st.subheader("✅ My Tasks")
if 'tasks' not in st.session_state:
    st.session_state.tasks = [f"Complete {weak_subject} assignment", "Review last 3 days of notes"]

new_task = st.text_input("Add a custom task...", placeholder="e.g., Read Chapter 4")
if st.button("Add Task"):
    if new_task:
        st.session_state.tasks.append(new_task)
        st.rerun()

for i, task in enumerate(st.session_state.tasks):
    col_t, col_b = st.columns([4, 1])
    col_t.checkbox(task, key=f"task_{i}")
    if col_b.button("🗑️", key=f"del_{i}"):
        st.session_state.tasks.pop(i)
        st.rerun()

render_footer()