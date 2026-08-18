import streamlit as st

def render_header():
    """Renders a consistent header/banner across all pages."""
    # You can add a custom logo or banner image here later if you want!
    st.markdown("""
        <div style='text-align: right; padding: 10px; color: gray; font-size: 14px;'>
            <i>🎓 AI Smart Planner Prototype</i>
        </div>
    """, unsafe_allow_html=True)

def render_footer():
    """Renders a consistent footer at the absolute bottom of the page."""
    st.divider() # Draws a neat horizontal line
    st.markdown("""
        <div style='text-align: center; color: gray; padding-top: 10px;'>
            <p>Built with ❤️ By Priyo Chand | Version 1.0.0</p>
            <p style='font-size: 12px;'>Powered by Python, Streamlit, and Machine Learning</p>
        </div>
    """, unsafe_allow_html=True)