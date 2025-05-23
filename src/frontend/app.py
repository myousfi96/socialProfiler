"""
Main Streamlit application for Social Profiler.
"""
import os
import sys
import streamlit as st

# Add project root to Python path to make absolute imports work
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now use absolute imports
from src.frontend.config import PAGE_TITLE, PAGE_LAYOUT
from src.frontend.styles import CUSTOM_CSS, SENTIMENT_LEGEND_HTML
from src.frontend.api import call_analyze_api
from src.frontend.visualizations import create_sentiment_chart, create_topics_chart
from src.frontend.components import display_persona_card, display_detailed_info


st.set_page_config(page_title=PAGE_TITLE, layout=PAGE_LAYOUT)


st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


with st.sidebar.form("profile_input_form"):
    st.header("Profile Input")
    username_input = st.text_input("Enter X Username (without @)", placeholder="")
    tweet_count_input = st.number_input(
        "Number of recent tweets to analyze", 
        min_value=1,  
        value=10
    )
    analyze_button = st.form_submit_button("Analyze Profile ✨")


st.title("Social Profiler 🤖")
st.caption("Analyze X (Twitter) profiles to gain insights into personality, interests, and more.")


if analyze_button and username_input:
    with st.spinner("Analyzing profile..."):
        analysis_results = call_analyze_api(username_input, tweet_count_input)
    
    if analysis_results and not analysis_results.get("error"):
        st.success(f"Successfully analyzed @{username_input}!")
        

        display_persona_card(analysis_results, username_input)
        

        st.markdown("---")
        st.subheader("😀 Sentiment Analysis")
        
        scaled = analysis_results.get("sentiment_scaled_score")
        if scaled is not None:
            fig = create_sentiment_chart(scaled)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown(SENTIMENT_LEGEND_HTML, unsafe_allow_html=True)
        else:
            st.info("Sentiment analysis not available.")
        

        st.markdown("---")
        st.subheader("📊 Top Topics")
        
        topic_scores = analysis_results.get("category_scores", {})
        if topic_scores:
            fig = create_topics_chart(topic_scores)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.caption("💡 Hover a spoke to see all tweets that generated this topic.")
        else:
            st.info("No topical signals detected.")
        

        display_detailed_info(analysis_results)
        
    else:
        st.error("⚠️ Failed to get analysis. Please check the logs or try again.")
