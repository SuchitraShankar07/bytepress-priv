import streamlit as st
from src.core.auth import register_user
from src.ui import topics  # use DB-backed starter topics

def registration_page():
    st.markdown("### Join thousands of readers! 📫")
    st.markdown("*Create your account to start receiving personalized news*")
    # initialize DB and get starter topics
    db = topics.init_db()
    starter = topics.list_topics(db, limit=9)

    # session storage for selected topics during registration (not persisted)
    sel_key = "reg_selected_topics"
    if sel_key not in st.session_state:
        st.session_state[sel_key] = []
    # cache for search-driven dropdown options
    st.session_state.setdefault("reg_topic_options", [])

    # Precompute index lookup for the 9 starter checkboxes (name -> index)
    name_to_idx = {t["name"]: i for i, t in enumerate(starter)}

    # PRE-SET checkbox states from the selected list BEFORE rendering widgets
    for idx, t in enumerate(starter):
        key = f"reg_starter_{idx}"
        # Keep checkbox state in sync with selection list
        st.session_state[key] = (t["name"] in st.session_state[sel_key])

    # Registration form in a nice container
    with st.container():
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("#### Account Details")
            name = st.text_input("👤 Full Name", placeholder="John Doe", help="We'll use this to personalize your experience")
            email = st.text_input("📧 Email Address", placeholder="your.email@example.com", help="We'll send your personalized news here")
            password = st.text_input("🔒 Password", type="password", placeholder="Choose a secure password", help="Minimum 6 characters recommended")
            st.markdown("")
            agree_terms = st.checkbox("I agree to receive personalized news emails")

        # Starter topics selection (not persisted)
        st.markdown("---")
        st.markdown("#### Pick some starter topics (not persisted)")
        cols = st.columns(3)
        for i, t in enumerate(starter):
            label = t["name"]
            with cols[i % 3]:
                key = f"reg_starter_{i}"
                checked = st.checkbox(label, key=key)
                if checked and label not in st.session_state[sel_key]:
                    st.session_state[sel_key].append(label)
                if not checked and label in st.session_state[sel_key]:
                    st.session_state[sel_key].remove(label)

        # Custom topic input (not persisted) -> search + dropdown from DB only
        st.markdown("")
        st.markdown("#### Add another topic from the database (optional)")
        # Text box with Search button next to it
        s1, sbtn = st.columns([4, 1])
        with s1:
            reg_search = st.text_input("Search topics", key="reg_topic_search").strip()
        with sbtn:
            if st.button("Search", key="reg_topic_search_btn"):
                # Build options from DB on demand (prefix, name-only), excluding already selected
                candidates = topics.search_topics_by_name_prefix(db, prefix=reg_search if reg_search else None)
                existing_names = set(st.session_state[sel_key])
                st.session_state["reg_topic_options"] = [t["name"] for t in candidates if t["name"] not in existing_names]

        # Results dropdown comes after search controls
        selected = st.selectbox(
            "Matches",
            st.session_state["reg_topic_options"] if st.session_state["reg_topic_options"] else ["No matches"],
            key="reg_topic_select"
        )
        if st.button("Add", key="reg_topic_add_btn", disabled=(selected == "No matches")):
            if selected != "No matches":
                if selected in st.session_state[sel_key]:
                    st.info("Already selected.")
                else:
                    # Same logic as checkbox: add to the selected list if not present
                    st.session_state[sel_key].append(selected)
                    # Remove from dropdown cache so it can't be added again without a new search
                    st.session_state["reg_topic_options"] = [
                        opt for opt in st.session_state.get("reg_topic_options", []) if opt != selected
                    ]
                    st.success(f"Added '{selected}' (not persisted).")

        # Show current selections
        if st.session_state[sel_key]:
            st.caption("Selected topics (session only): " + ", ".join(st.session_state[sel_key]))
        else:
            st.caption("No topics selected yet.")

        st.markdown("---")
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
                            # Placeholder only: topics not persisted yet
                            st.info("📝 Your topic preferences will be saved soon (not persisted in this version).")
                            # Redirect to Home with login prompt
                            st.session_state["flash_success"] = "Registration successful. Please log in."
                            st.session_state.page = 'home'
                            st.query_params.update(page='home')
                            st.rerun()
                        else:
                            if result["error_type"] == "user_exists":
                                st.error("❌ This email is already registered.")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("🔐 Login Instead", type="primary"):
                                        st.session_state.page = 'login'
                                        st.rerun()
                                with col2:
                                    st.info("Use the login page to access your account.")
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
