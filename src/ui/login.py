import streamlit as st
from src.core.auth import authenticate_user

def login_page():
    st.markdown("### Welcome back! 👋")
    st.markdown("*Sign in to access your personalized news*")
    
    # Login form in a nice container
    with st.container():
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Form fields with better styling
            st.markdown("#### Sign In")
            
            email = st.text_input("📧 Email Address", 
                                placeholder="your.email@example.com",
                                help="Enter your registered email address")
            
            password = st.text_input("🔒 Password", 
                                   type="password",
                                   placeholder="Enter your password",
                                   help="Enter your account password")
            
            # Add some spacing
            st.markdown("")
            
            # Remember me option
            remember_me = st.checkbox("Remember me")
            
        # Login button - full width and prominent
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔐 Sign In", type="primary", use_container_width=True):
                if not email or not password:
                    st.warning("⚠️ Please fill in all fields.")
                elif "@" not in email or "." not in email:
                    st.warning("⚠️ Please enter a valid email address.")
                else:
                    with st.spinner("Signing you in..."):
                        user_data = authenticate_user(email.strip().lower(), password)
                        
                        if user_data:
                            # Store user data in session state
                            st.session_state.logged_in = True
                            st.session_state.user_data = user_data
                            st.session_state.user_email = user_data['email']
                            st.session_state.user_name = user_data.get('name', 'User')
                            
                            st.success(f"🎉 Welcome back, {st.session_state.user_name}!")
                            st.balloons()
                            
                            # Automatically redirect to dashboard after login
                            st.session_state.page = 'dashboard'
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password. Please try again.")
    
    # Additional options
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🆕 New to Bytepress?**")
        if st.button("Create Account", use_container_width=True):
            st.session_state.page = 'register'
            st.rerun()
    
    with col2:
        st.markdown("**🔑 Forgot Password?**")
        if st.button("Reset Password", use_container_width=True):
            st.info("💡 Password reset feature coming soon!")

def check_authentication():
    """Check if user is authenticated"""
    return st.session_state.get('logged_in', False)

def logout_user():
    """Logout user and clear session"""
    # Clear all user-related session state
    keys_to_clear = ['logged_in', 'user_data', 'user_email', 'user_name']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.session_state.page = 'home'
    st.success("👋 You've been logged out successfully!")
    st.rerun()

def get_current_user():
    """Get current logged in user data"""
    if check_authentication():
        return st.session_state.get('user_data', {})
    return None