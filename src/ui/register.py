import streamlit as st
from src.core.auth import register_user

def registration_page():
    st.markdown("### Join thousands of readers! 📫")
    st.markdown("*Create your account to start receiving personalized news*")
    
    # Registration form in a nice container
    with st.container():
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Form fields with better styling
            st.markdown("#### Account Details")
            
            name = st.text_input("👤 Full Name", 
                               placeholder="John Doe",
                               help="We'll use this to personalize your experience")
            
            email = st.text_input("📧 Email Address", 
                                placeholder="your.email@example.com",
                                help="We'll send your personalized news here")
            
            password = st.text_input("🔒 Password", 
                                   type="password",
                                   placeholder="Choose a secure password",
                                   help="Minimum 6 characters recommended")
            
            # Add some spacing
            st.markdown("")
            
            # Terms and conditions - require agreement before showing the register button
            agree_terms = st.checkbox("I agree to receive personalized news emails")

        # Registration button - full width and prominent
        st.markdown("")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Create My Account", type="primary", use_container_width=True):
                if not name or not email or not password:
                    st.warning("⚠️ Please fill in all fields.")
                elif not agree_terms:
                    st.warning("⚠️ Please agree to receive emails to continue.")
                elif len(password) < 6:
                    st.warning("⚠️ Password should be at least 6 characters.")
                elif "@" not in email or "." not in email:
                    st.warning("⚠️ Please enter a valid email address.")
                elif len(name.strip()) < 2:
                    st.warning("⚠️ Please enter your full name.")
                else:
                    with st.spinner("Creating your account..."):
                        result = register_user(email.strip().lower(), password, name.strip())
                        
                        if result["success"]:
                            st.success(f"🎉 Welcome to Bytepress, {name.split()[0]}! Registration successful!")
                            st.balloons()
                            st.info("💡 You can now start customizing your news preferences.")
                        else:
                            # Handle specific error types
                            if result["error_type"] == "user_exists":
                                st.error("❌ This email is already registered.")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("🔐 Login Instead", type="primary"):
                                        st.session_state.page = 'login'
                                        st.rerun()
                                with col2:
                                    st.info("Use the login page to access your account.")
                            elif result["error_type"] == "database_error":
                                st.error("😔 Something went wrong. Please try again later.")
                                st.caption(f"Error details: {result['error']}")
                            else:
                                st.error("😔 Something went wrong. Please try again later.")
    
    # Additional info
    st.markdown("---")
    
    # Login option for existing users
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**👋 Already have an account?**")
        if st.button("🔐 Sign In Instead", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
    
    with col2:
        st.markdown("**❓ Need help?**")
        st.markdown("Contact support for assistance")
    
    st.markdown("---")
    st.markdown("### What happens next?")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🎯 Personalization**\n\nChoose your favorite topics and sources")
    with col2:
        st.markdown("**📬 Daily Digest**\n\nReceive curated news every morning")
