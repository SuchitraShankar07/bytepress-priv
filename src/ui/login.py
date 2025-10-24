import streamlit as st
from src.core.auth import authenticate_user
from src.core.database import get_user  # to rebuild user_data from query params

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
                            # Ensure a user_id is present in session (ObjectId -> str; fallback to email)
                            st.session_state.user_id = str(user_data.get('_id') or user_data['email'])
                            
                            st.success(f"🎉 Welcome back, {st.session_state.user_name}!")
                            
                            # Persist session to URL (no experimental API)
                            st.query_params.update(
                                page='dashboard',
                                user_email=st.session_state.user_email,
                                user_name=st.session_state.user_name,
                                user_id=st.session_state.user_id,
                            )
                            st.balloons()
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
    """Check if user is authenticated; rebuild from URL params if needed"""
    if st.session_state.get('logged_in', False):
        return True

    # Rebuild state from URL query params on reload
    qp = st.query_params
    email = qp.get('user_email')
    name = qp.get('user_name')
    uid = qp.get('user_id')

    # Normalize values (support both list and str)
    if isinstance(email, list):
        email = email[0]
    if isinstance(name, list):
        name = name[0]
    if isinstance(uid, list):
        uid = uid[0]

    if email:
        user = get_user(email) or {"email": email, "name": name or "User", "_id": uid or email}
        st.session_state['logged_in'] = True
        st.session_state['user_data'] = user
        st.session_state['user_email'] = user.get('email', email)
        st.session_state['user_name'] = user.get('name', name or "User")
        st.session_state['user_id'] = str(user.get('_id') or uid or email)
        return True

    return False

def logout_user():
    """Logout user and clear session"""
    # Clear all user-related session state
    for key in ['logged_in', 'user_data', 'user_email', 'user_name', 'user_id']:
        st.session_state.pop(key, None)
    
    # Remove user_* params then set page=home (no experimental API)
    for k in ('user_email', 'user_name', 'user_id'):
        st.query_params.pop(k, None)
    st.query_params.update(page='home')
    st.success("👋 You've been logged out successfully!")
    st.rerun()

def get_current_user():
    """Get current logged in user data"""
    if check_authentication():
        return st.session_state.get('user_data', {})
    return None