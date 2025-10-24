# python
# FILE: src/ui/topics.py

import pymongo
from typing import List, Optional
import streamlit as st
import re
from datetime import datetime
from src.utils.config import MONGODB_URI, DATABASE_NAME  # type: ignore

TOPICS_COLL = "topics"
ARTICLES_COLL = "articles"


def get_db():
    client = pymongo.MongoClient(MONGODB_URI, serverSelectionTimeoutMS=20000, connectTimeoutMS=20000)
    # test connection (may raise)
    client.admin.command("ping")
    return client[DATABASE_NAME]


def init_db(db=None):
    if db is None:
        db = get_db()
    # Ensure indexes
    db[TOPICS_COLL].create_index([("name", 1)], unique=True, background=True)
    db[ARTICLES_COLL].create_index([("topic_id", 1)], background=True)
    seed_topics_and_articles(db)  # seed starter data for display
    return db


def seed_topics_and_articles(db):
    # Only seed when no topics exist
    if db[TOPICS_COLL].count_documents({}) > 0:
        return

    topics = [
        {"name": "Technology", "description": "Latest in tech, gadgets, and AI", "created_at": datetime.utcnow()},
        {"name": "Business", "description": "Markets, startups, and finance", "created_at": datetime.utcnow()},
        {"name": "Sports", "description": "Scores, events, and analysis", "created_at": datetime.utcnow()},
        {"name": "Health", "description": "Wellness, medicine, and research", "created_at": datetime.utcnow()},
        {"name": "Entertainment", "description": "Movies, TV, and culture", "created_at": datetime.utcnow()},
        {"name": "Science", "description": "Research and discoveries", "created_at": datetime.utcnow()},
        {"name": "Travel", "description": "Destinations and tips", "created_at": datetime.utcnow()},
        {"name": "Food", "description": "Recipes, restaurants and reviews", "created_at": datetime.utcnow()},
        {"name": "Education", "description": "Learning and policy", "created_at": datetime.utcnow()},
        {"name": "Politics", "description": "Government and policy", "created_at": datetime.utcnow()},
    ]
    db[TOPICS_COLL].insert_many(topics)
    topic_docs = list(db[TOPICS_COLL].find({}, {"name": 1}))
    sample_articles = []
    for td in topic_docs:
        tid = td["_id"]
        name = td["name"]
        for i in range(1, 4):
            sample_articles.append({
                "topic_id": tid,
                "title": f"{name} Article {i}",
                "content": f"Sample content for {name} article {i}.",
                "created_at": datetime.utcnow()
            })
    if sample_articles:
        db[ARTICLES_COLL].insert_many(sample_articles)


def list_topics(db=None, search: Optional[str] = None, limit: Optional[int] = None) -> List[dict]:
    if db is None:
        db = get_db()
    q = {}
    if search:
        pattern = re.compile(re.escape(search), re.IGNORECASE)
        q = {"$or": [{"name": pattern}, {"description": pattern}]}
    cursor = db[TOPICS_COLL].find(q).sort("name", pymongo.ASCENDING)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)


def search_topics_by_name_prefix(db=None, prefix: Optional[str] = None, limit: Optional[int] = None) -> List[dict]:
    """
    Search topics by name only, anchored at the beginning (prefix match), case-insensitive.
    This avoids matching description text and inner substrings.
    """
    if db is None:
        db = get_db()
    if not prefix:
        cursor = db[TOPICS_COLL].find({}).sort("name", pymongo.ASCENDING)
        if limit:
            cursor = cursor.limit(limit)
        return list(cursor)
    pattern = re.compile(rf"^{re.escape(prefix)}", re.IGNORECASE)
    cursor = db[TOPICS_COLL].find({"name": pattern}).sort("name", pymongo.ASCENDING)
    if limit:
        cursor = cursor.limit(limit)
    return list(cursor)


def get_article_count(db=None, topic_id=None) -> int:
    if db is None:
        db = get_db()
    if topic_id is None:
        return 0
    return db[ARTICLES_COLL].count_documents({"topic_id": topic_id})


def get_articles_for_topic(db=None, topic_id=None) -> List[dict]:
    if db is None:
        db = get_db()
    if topic_id is None:
        return []
    return list(db[ARTICLES_COLL].find({"topic_id": topic_id}).sort("created_at", pymongo.DESCENDING))


# NOTE: Persistence of user <-> topic selections has been removed.
# Selections are kept only in Streamlit session_state. This function
# returns the in-memory (session) selection for a user.
def get_user_topics(db=None, user_id: int = None) -> List[str]:
    if user_id is None:
        return st.session_state.get("pre_registration_topics", [])
    return st.session_state.get(f"user_topics_{user_id}", [])


# Placeholder for future persistence implementation.
def persist_user_topics_placeholder(db=None, user_id: Optional[int] = None, topic_ids: List = None):
    """
    Placeholder: when persistence is desired, implement DB writes here.
    Currently does nothing to enforce non-persistence of selections.
    """
    return


def safe_rerun():
    """
    Robust rerun helper for current Streamlit versions.
    """
    try:
        st.rerun()
    except Exception:
        try:
            from streamlit.runtime.scriptrunner.script_runner import RerunException
            raise RerunException(rerun_data=None)
        except ImportError:
            st.session_state.setdefault("_rerun_requested", True)
            return


def topics_selector_ui(db=None, user_id: Optional[int] = None, register_mode: bool = False):
    """
    Show search box; when content changes display matching topic tags (checkboxes).
    When search empty, display up to 9 tags. Selections live in session_state only.
    """
    try:
        if db is None:
            db = init_db()
    except Exception as e:
        st.error("Could not connect to MongoDB for topics. Ensure MONGODB_URI and DB are reachable.")
        st.exception(e)
        return

    st.markdown("## 🔎 Browse & Select Topics")

    # keys
    search_key = f"topic_search_{user_id}" if user_id is not None else "topic_search_pre"
    labels_key = f"user_topics_labels_{user_id}" if user_id is not None else "pre_registration_topics_labels"
    ids_key = f"user_topics_{user_id}" if user_id is not None else "pre_registration_topics"

    # ensure session keys exist
    if labels_key not in st.session_state:
        st.session_state[labels_key] = []
    if ids_key not in st.session_state:
        st.session_state[ids_key] = []

    # search input
    search = st.text_input("Search topics", value="", key=search_key).strip()

    # get matching topics (or top 9 when empty)
    if search:
        matched = list_topics(db, search=search)
    else:
        matched = list_topics(db, search=None, limit=9)

    # build labels and map to ids (use full list so labels persist across searches)
    all_topics = list_topics(db, search=None)
    label_to_id = {f"{t['name']} — {t.get('description','')}": t["_id"] for t in all_topics}
    displayed_labels = [f"{t['name']} — {t.get('description','')}" for t in matched]

    st.markdown("### Choose topics")
    if not displayed_labels:
        st.info("No topics match your search.")
    else:
        cols = st.columns(3)
        for i, lbl in enumerate(displayed_labels):
            col = cols[i % 3]
            chk_key = f"{labels_key}_chk_{i}_{'u' if user_id else 'p'}"
            default = lbl in st.session_state[labels_key]
            checked = col.checkbox(lbl, value=default, key=chk_key)
            if checked and lbl not in st.session_state[labels_key]:
                st.session_state[labels_key].append(lbl)
                st.session_state[ids_key].append(label_to_id.get(lbl))
            if not checked and lbl in st.session_state[labels_key]:
                idx = st.session_state[labels_key].index(lbl)
                st.session_state[labels_key].pop(idx)
                try:
                    st.session_state[ids_key].pop(idx)
                except Exception:
                    tid = label_to_id.get(lbl)
                    if tid in st.session_state[ids_key]:
                        st.session_state[ids_key].remove(tid)

    # show current selection
    st.markdown("### Selected topics")
    if st.session_state[labels_key]:
        for lbl in st.session_state[labels_key]:
            st.write(f"- {lbl}")
    else:
        st.info("No topics selected yet.")

    # Save automatically when topics are selected
    if not register_mode:
        persist_user_topics_placeholder(db, user_id, st.session_state[ids_key])
        st.success("Topics saved for this session (not persisted).")
        st.info("Selections are stored only in this Streamlit session.")


def topics_page(db=None):
    try:
        if db is None:
            db = init_db()
    except Exception as e:
        st.error("Could not connect to MongoDB to show topics.")
        st.exception(e)
        return

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("You must register and sign in to view and manage topics.")
        return

    st.markdown("# 🗂️ Topics")
    st.markdown("Search available topics and view articles attached to each topic.")
    search = st.text_input("Search topics", value="")
    topics_list = list_topics(db, search=search.strip() if search else None)

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("Edit My Topics"):
            topics_selector_ui(db=db, user_id=user_id)

    for t in topics_list:
        article_count = get_article_count(db, t["_id"])
        with st.expander(f"{t['name']} — {article_count} articles"):
            st.write(t.get("description", ""))
            articles = get_articles_for_topic(db, t["_id"])
            for a in articles:
                st.subheader(a.get("title"))
                st.write(a.get("content"))


def manage_topics_page(db=None):
    """
    Page to add or remove topics, visible only when the user is logged in.
    Edits are NOT persisted; they modify a session-local snapshot only.
    """
    try:
        if db is None:
            db = init_db()
    except Exception as e:
        st.error("Could not connect to MongoDB to manage topics.")
        st.exception(e)
        return

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("You must register and sign in to manage topics.")
        return

    st.markdown("# 🛠️ Manage Topics")
    st.caption("Changes here are not saved to the database (session only).")

    # Create a session snapshot from DB (first time only)
    if "_temp_topics" not in st.session_state:
        st.session_state["_temp_topics"] = list_topics(db)

    # Initialize caches for search results
    st.session_state.setdefault("manage_add_options_labels", [])
    st.session_state.setdefault("manage_add_label_to_id", {})
    st.session_state.setdefault("manage_add_id_to_doc", {})

    # Add new topic (session only) via search + dropdown (DB topics only)
    st.subheader("Add Topic from Database (not persisted)")
    # Search input with button next to it
    sc, bc = st.columns([4, 1])
    with sc:
        search = st.text_input("Search topics", key="manage_add_search").strip()
    with bc:
        if st.button("Search", key="manage_add_search_btn", use_container_width=True):
            candidates = search_topics_by_name_prefix(db, prefix=search if search else None)
            existing_ids = {str(t.get("_id")) for t in st.session_state["_temp_topics"]}
            options = [
                (str(t["_id"]), f"{t['name']} — {t.get('description','')}")
                for t in candidates
                if str(t["_id"]) not in existing_ids
            ]
            st.session_state["manage_add_options_labels"] = [lbl for (_id, lbl) in options]
            st.session_state["manage_add_label_to_id"] = {lbl: _id for (_id, lbl) in options}
            st.session_state["manage_add_id_to_doc"] = {
                str(t["_id"]): {"_id": t["_id"], "name": t["name"], "description": t.get("description", "")}
                for t in candidates if str(t["_id"]) not in existing_ids
            }

    # Results dropdown comes after the search controls
    label_options = st.session_state["manage_add_options_labels"] or ["No matches"]
    selected_label = st.selectbox("Matches", label_options, key="manage_add_select")
    if st.button("Add", key="manage_add_btn", use_container_width=True, disabled=(selected_label == "No matches")):
        if selected_label != "No matches":
            sel_id = st.session_state["manage_add_label_to_id"].get(selected_label)
            sel_doc = st.session_state["manage_add_id_to_doc"].get(sel_id)
            if sel_doc:
                # Prevent duplicates by _id
                if any(str(t.get("_id")) == sel_id for t in st.session_state["_temp_topics"]):
                    st.info("Already added.")
                else:
                    st.session_state["_temp_topics"].append(sel_doc)
                    # Remove from cached options so it can't be added again without a new search
                    st.session_state["manage_add_options_labels"] = [
                        lbl for lbl in st.session_state.get("manage_add_options_labels", []) if lbl != selected_label
                    ]
                    st.session_state["manage_add_label_to_id"].pop(selected_label, None)
                    st.session_state["manage_add_id_to_doc"].pop(sel_id, None)
                    st.success(f"Added '{sel_doc['name']}' (not persisted).")
                    st.rerun()

    # Remove existing topics (session only)
    st.subheader("Existing Topics (session snapshot)")
    temp_topics = st.session_state["_temp_topics"]
    if not temp_topics:
        st.info("No topics to show.")
        return

    cols = st.columns(3)
    for i, topic in enumerate(temp_topics):
        with cols[i % 3]:
            with st.container():
                col1, col2 = st.columns([8, 2])
                with col1:
                    st.write(topic["name"])
                with col2:
                    if st.button("❌", key=f"remove_temp_{i}"):
                        removed = st.session_state["_temp_topics"].pop(i)
                        st.success(f"Removed '{removed['name']}' (not persisted).")
                        st.rerun()


# Helper to attach pre-registration topics to session for a user (no DB writes)
def attach_pre_registration_topics(db, user_id: int):
    selected = st.session_state.get("pre_registration_topics", [])
    labels = st.session_state.get("pre_registration_topics_labels", [])
    if selected:
        # move choices into the user's session-scoped selection (still not persisted)
        st.session_state[f"user_topics_{user_id}"] = selected
        st.session_state[f"user_topics_labels_{user_id}"] = labels
        # clear temporary registration keys
        st.session_state.pop("pre_registration_topics", None)
        st.session_state.pop("pre_registration_topics_labels", None)


# Example helper to create a user (used by registration flow elsewhere)
def create_user(db, email: str) -> int:
    if db is None:
        db = get_db()
    try:
        result = db["users"].insert_one({"email": email})
        return result.inserted_id
    except pymongo.errors.DuplicateKeyError:
        user = db["users"].find_one({"email": email})
        if user:
            return user["_id"]
        raise


# If module run directly, initialize DB (useful for dev)
if __name__ == "__main__":
    init_db()
    print("DB initialized at", MONGODB_URI)

# Add the manage topics page to the side panel
if "user_id" in st.session_state:
    st.sidebar.title("Navigation")
    st.sidebar.button("Topics", on_click=lambda: manage_topics_page())