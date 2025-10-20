import streamlit as st
from src.ui.login import logout_user, get_current_user

def dashboard_page():
    user = get_current_user()
    
    if not user:
        st.error("Please log in to access the dashboard.")
        st.session_state.page = 'login'
        st.rerun()
        return
    
    # Header with user info
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"# 👋 Welcome back, {user.get('name', 'User')}!")
        st.markdown("### Your Personalized News Dashboard")
    
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
    
    st.markdown("---")
    
    # Simple dashboard content - just account info for login functionality
    st.markdown("## 📋 Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(f"""
        **Name:** {user.get('name', 'Not provided')}
        
        **Email:** {user.get('email', 'Not provided')}
        
        **Member since:** {str(user.get('created_at', 'Unknown'))[:10]}
        """)
    
    with col2:
        st.markdown("### � Successfully Logged In!")
        st.success("✅ You are now logged into your Bytepress account.")
        st.info("💡 Additional features will be available soon.")
