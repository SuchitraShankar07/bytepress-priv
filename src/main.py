import streamlit as st
from src.ui.register import registration_page

st.set_page_config(page_title="Bytepress", layout="centered")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Sidebar navigation (keep for power users)
st.sidebar.title("🧭 Navigation")
sidebar_choice = st.sidebar.selectbox("Quick Navigation", ["Home", "Register"], 
                                     index=0 if st.session_state.page == 'home' else 1)

# Update session state based on sidebar
if sidebar_choice == "Home":
    st.session_state.page = 'home'
elif sidebar_choice == "Register":
    st.session_state.page = 'register'

# Main content
if st.session_state.page == 'home':
    # Header with better styling
    st.markdown("# 📰 Bytepress")
    st.markdown("### *Your Personalized News Companion*")
    
    # Hero section
    st.markdown("---")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        **Welcome to Bytepress!** 
        
        Get personalized news delivered straight to your inbox based on your interests and preferences. 
        Stay informed without the overwhelm.
        
        ✨ **Features:**
        - 📧 Personalized email newsletters
        - 🎯 Topic-based filtering
        - ⏰ Customizable delivery schedule
        - 📱 Mobile-friendly content
        """)
    
    with col2:
        st.markdown("### 🎯 Quick Actions")
        
        # Main CTA buttons
        if st.button("🚀 Get Started", type="primary", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()
            
        if st.button("📋 Register Now", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()
    
    # Additional info section
    st.markdown("---")
    st.markdown("### How It Works")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**1️⃣ Sign Up**\n\nCreate your account and tell us your interests")
    with col2:
        st.markdown("**2️⃣ Customize**\n\nChoose topics, frequency, and preferences")
    with col3:
        st.markdown("**3️⃣ Enjoy**\n\nReceive curated news in your inbox")
    
    # Footer
    st.markdown("---")
    st.markdown("*Built for the SE project* 💙")

elif st.session_state.page == 'register':
    # Add a back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.rerun()
    
    with col2:
        st.markdown("# 📝 Create Your Account")
    
    registration_page()
