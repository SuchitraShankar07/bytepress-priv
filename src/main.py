import streamlit as st
from src.ui.register import registration_page
from src.ui.login import login_page, check_authentication, logout_user, get_current_user
from src.ui.dashboard import dashboard_page

st.set_page_config(page_title="Bytepress", layout="centered")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

# Check if user is logged in for navigation purposes
is_logged_in = check_authentication()
current_user = get_current_user()

# Sidebar navigation
st.sidebar.title("🧭 Navigation")

if is_logged_in:
    # Logged in user navigation
    st.sidebar.markdown(f"👋 Welcome, **{current_user.get('name', 'User')}**!")
    
    nav_options = ["Dashboard", "Home", "Logout"]
    default_index = 0 if st.session_state.page == 'dashboard' else (1 if st.session_state.page == 'home' else 0)
    sidebar_choice = st.sidebar.selectbox("Quick Navigation", nav_options, index=default_index)
    
    # Handle navigation
    if sidebar_choice == "Dashboard":
        st.session_state.page = 'dashboard'
    elif sidebar_choice == "Home":
        st.session_state.page = 'home'
    elif sidebar_choice == "Logout":
        logout_user()
        
else:
    # Guest user navigation
    nav_options = ["Home", "Login", "Register"]
    current_index = 0 if st.session_state.page == 'home' else (1 if st.session_state.page == 'login' else 2)
    sidebar_choice = st.sidebar.selectbox("Quick Navigation", nav_options, index=current_index)
    
    # Handle navigation
    if sidebar_choice == "Home":
        st.session_state.page = 'home'
    elif sidebar_choice == "Login":
        st.session_state.page = 'login'
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
        
        if is_logged_in:
            # Logged in user actions
            if st.button("� Go to Dashboard", type="primary", use_container_width=True):
                st.session_state.page = 'dashboard'
                st.rerun()
        else:
            # Guest user actions
            if st.button("🔐 Sign In", type="primary", use_container_width=True):
                st.session_state.page = 'login'
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

elif st.session_state.page == 'login':
    # Add a back button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("← Back to Home"):
            st.session_state.page = 'home'
            st.rerun()
    
    with col2:
        st.markdown("# 🔐 Sign In to Your Account")
    
    login_page()

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

elif st.session_state.page == 'dashboard':
    # Dashboard page (only accessible if logged in)
    if is_logged_in:
        dashboard_page()
    else:
        st.error("🔒 Please log in to access the dashboard.")
        st.session_state.page = 'login'
        st.rerun()
