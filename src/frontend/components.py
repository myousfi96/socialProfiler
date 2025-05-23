"""
Reusable UI components for the application.
"""
import streamlit as st
from .styles import render_tags

def display_persona_card(analysis_results, username_input):
    """
    Display the persona snapshot section.
    
    Args:
        analysis_results: Analysis data from API
        username_input: The username entered by the user
    """
    st.subheader("🎭 Persona Snapshot")
    
    with st.container():
        # Top row: avatar + name
        col_img, col_info = st.columns([1, 4])
        
        # Profile image
        with col_img:
            url = analysis_results.get("user_profile_image_url")
            st.image(url or "https://via.placeholder.com/110/007ACC/FFFFFF?Text=User", width=80)
        
        # User info
        with col_info:
            display_name = analysis_results.get("user_display_name") or analysis_results.get("username", username_input)
            st.markdown(f"### {display_name}")
            st.caption(f"@{analysis_results.get('username', username_input)}")
            
            bio = analysis_results.get("user_bio")
            if bio:
                st.caption(f"*{bio[:120]}{'…' if len(bio) > 120 else ''}*")
        
        st.markdown("---")
        
        # MBTI & Interests columns
        col_mbti, col_keywords = st.columns(2)
        
        # MBTI personality
        with col_mbti:
            st.markdown("##### 🧠 Personality (MBTI)")
            mbti = analysis_results.get("mbti_result", {})
            if mbti:
                st.markdown(f"**{mbti.get('mbti_name','Unknown')}**  \n{mbti.get('mbti_code','')}")
                st.write(mbti.get("mbti_portrait", "—"))
                with st.expander("See why we guessed this"):
                    st.write(mbti.get("rationale", "No rationale provided."))
            else:
                st.info("Personality insight not available.")
        
        # Top interests
        with col_keywords:
            st.markdown("##### 🔑 Top Interests")
            top_keywords = analysis_results.get("top_keywords", [])
            if top_keywords:
                tags_html = render_tags(top_keywords)
                st.markdown(tags_html, unsafe_allow_html=True)
            else:
                st.info("No interests detected.")

def display_detailed_info(analysis_results):
    """
    Display the detailed information section with bio and tweets.
    
    Args:
        analysis_results: Analysis data from API
    """
    st.markdown("---")
    st.subheader("📜 Detailed Information")
    
    with st.expander("View Bio & Recent Tweets"):
        bio_text = analysis_results.get("user_bio")
        if bio_text:
            st.markdown("**User Bio**")
            st.text_area("Bio", bio_text, height=100, disabled=True, label_visibility="collapsed")
        else:
            st.markdown("**User Bio:** Not available.")
        
        tweets = analysis_results.get("recent_tweets", [])
        if tweets:
            st.markdown("**Recent Tweets (Sample)**")
            for tw in tweets:
                st.markdown(f"<div class='tweet-card'>{tw}</div>", unsafe_allow_html=True)
        else:
            st.markdown("**Recent Tweets:** Not available.") 