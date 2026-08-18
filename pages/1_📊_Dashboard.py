import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.db_functions import get_user_history, get_user_profile
from utils.ui import render_header, render_footer

# 1. Access Control
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.warning("🔒 Please log in to view your dashboard.")
    st.stop()

render_header()

# 2. Fetch Data
username = st.session_state['username']
df = get_user_history(username)
profile = get_user_profile(username)
display_name = profile[0] if profile and profile[0] else username

st.title(f"📊 Semester Mission Control")

# --- SCENARIO: NEW USER (NO DATA) ---
if df.empty:
    st.info("👋 Welcome! Log your first study sessions to see your Semester Outlook.")
    if st.button("🚀 Start Logging"):
        st.switch_page("pages/2_📝_Log_Study.py")
    st.stop()

# --- DATA AGGREGATION ---
df['log_date'] = pd.to_datetime(df['log_date'])
semester_df = df.groupby('log_date').agg({
    'study_hours': 'sum',
    'predicted_marks': 'mean',
    'focus_score': 'mean'
}).reset_index().sort_values('log_date')

# --- 🛡️ FIX 1: SAFETY CHECK FOR DELTA CALCULATION ---
current_score = semester_df['predicted_marks'].iloc[-1]
if len(semester_df) > 1:
    prev_score = semester_df['predicted_marks'].iloc[-2]
    delta = round(current_score - prev_score, 1)
else:
    delta = 0.0 # No change possible with only one data point

# 3. KPI METRICS
m1, m2, m3 = st.columns(3)
m1.metric("📚 Semester Study", f"{semester_df['study_hours'].sum():.1f} Hrs")
m2.metric("🎓 Semester Outlook", f"{current_score:.1f}%", f"{delta}%" if len(semester_df) > 1 else None)
m3.metric("🧠 Avg Focus", f"{semester_df['focus_score'].mean():.1f}/5")

# Status Message
if len(semester_df) > 1:
    if delta > 0: st.success("🔥 You are on an upward trend!")
    elif delta < 0: st.error("⚠️ Performance is dipping. Time to focus!")
    else: st.info("⚖️ Your performance is stable.")
else:
    st.info("📈 Log another session tomorrow to see your performance trend!")

st.divider()

# 4. THE SEMESTER WAVE
st.subheader("🌊 Semester Performance Wave")

# --- 🛡️ FIX 2: CONDITIONAL CHART RENDERING ---
if len(semester_df) < 2:
    st.warning("💡 The 'Wave' needs at least 2 days of data to show a trend. Keep studying!")
    # Show a simple marker for the single day
    fig_wave = px.scatter(semester_df, x='log_date', y='predicted_marks', size_max=20)
else:
    fig_wave = go.Figure()
    # Add Target Line
    fig_wave.add_trace(go.Scatter(
        x=semester_df['log_date'], y=[80] * len(semester_df),
        mode='lines', name='Target (80%)',
        line=dict(color='rgba(0,0,0,0.2)', width=2, dash='dot'), hoverinfo='skip'
    ))
    # Add Wave
    fig_wave.add_trace(go.Scatter(
        x=semester_df['log_date'], y=semester_df['predicted_marks'],
        mode='lines+markers', name='Semester Avg',
        line=dict(shape='spline', smoothing=1.3, width=5, color='#FF4B4B'),
        marker=dict(size=10, color='#FF4B4B', line=dict(width=2, color='white')),
        fill='tozeroy', fillcolor='rgba(255, 75, 75, 0.1)'
    ))

fig_wave.update_layout(
    height=400, margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(showgrid=False),
    yaxis=dict(title="Predicted %", range=[0, 105], gridcolor='rgba(0,0,0,0.05)'),
    plot_bgcolor='rgba(0,0,0,0)', hovermode="x unified", showlegend=False
)
st.plotly_chart(fig_wave, use_container_width=True)

# 5. SUBJECTS & STATS
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("### 🔍 Time Investment")
    subj_data = df.groupby('subject')['study_hours'].sum().reset_index()
    fig_pie = px.pie(subj_data, values='study_hours', names='subject', hole=0.5,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=300)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.markdown("### 🏆 Achievement")
    st.write("<br>", unsafe_allow_html=True)
    if not subj_data.empty:
        top = subj_data.loc[subj_data['study_hours'].idxmax(), 'subject']
        st.info(f"**Major Focus:**\n\n{top}")
    
    progress = min(semester_df['study_hours'].sum() / 100, 1.0)
    st.write(f"**Semester Goal (100 hrs):**")
    st.progress(progress)

st.divider()

# 6. HISTORY TABLE
with st.expander("📜 View Full Study History"):
    st.dataframe(df[['log_date', 'subject', 'study_hours', 'focus_score', 'predicted_marks']]
                 .sort_values('log_date', ascending=False), use_container_width=True, hide_index=True)

render_footer()