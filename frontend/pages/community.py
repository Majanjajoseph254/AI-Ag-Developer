import streamlit as st
from datetime import datetime
from backend.db import execute_query, fetch_all, fetch_one

CATEGORIES = ["General", "Crop Tips", "Disease Help", "Market Info", "Weather", "Equipment", "Livestock", "Other"]


def show_community():
    st.title("👥 Community Forum")
    st.markdown("Connect with fellow farmers, share knowledge, and ask questions.")

    user = st.session_state.get("user")
    if not user:
        st.warning("Please log in to access the community forum.")
        return

    if "view_post_id" in st.session_state and st.session_state["view_post_id"]:
        _show_post_detail(user)
        return

    tab1, tab2 = st.tabs(["📋 Forum Posts", "✏️ Create New Post"])

    with tab1:
        _show_posts_list(user)

    with tab2:
        _show_create_post(user)


def _show_posts_list(user):
    category_filter = st.selectbox("Filter by Category", ["All"] + CATEGORIES)

    if category_filter == "All":
        posts = fetch_all(
            "SELECT cp.*, u.name as author_name FROM community_posts cp JOIN users u ON cp.user_id = u.id ORDER BY cp.created_at DESC"
        )
    else:
        posts = fetch_all(
            "SELECT cp.*, u.name as author_name FROM community_posts cp JOIN users u ON cp.user_id = u.id WHERE cp.category = %s ORDER BY cp.created_at DESC",
            (category_filter,)
        )

    if not posts:
        st.info("No posts yet. Be the first to start a discussion!")
        return

    for post in posts:
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                category_emoji = {
                    "General": "💬", "Crop Tips": "🌱", "Disease Help": "🔬",
                    "Market Info": "📊", "Weather": "🌦️", "Equipment": "🔧",
                    "Livestock": "🐄", "Other": "📌"
                }
                emoji = category_emoji.get(post.get("category", ""), "💬")
                st.markdown(f"### {emoji} {post['title']}")
                st.caption(f"By **{post['author_name']}** | {post.get('category', 'General')} | {post['created_at'].strftime('%b %d, %Y %H:%M') if post.get('created_at') else ''}")
                content_preview = post["content"][:200] + "..." if len(post["content"]) > 200 else post["content"]
                st.markdown(content_preview)
            with col2:
                reply_count = fetch_one(
                    "SELECT COUNT(*) as cnt FROM community_replies WHERE post_id = %s",
                    (post["id"],)
                )
                count = reply_count["cnt"] if reply_count else 0
                st.markdown(f"💬 **{count}** replies")
                if st.button("View", key=f"view_{post['id']}"):
                    st.session_state["view_post_id"] = post["id"]
                    st.rerun()
                if post["user_id"] == user["id"]:
                    if st.button("🗑️ Delete", key=f"del_{post['id']}"):
                        execute_query("DELETE FROM community_replies WHERE post_id = %s", (post["id"],))
                        execute_query("DELETE FROM community_posts WHERE id = %s", (post["id"],))
                        st.success("Post deleted.")
                        st.rerun()
            st.divider()


def _show_create_post(user):
    with st.form("new_post_form"):
        title = st.text_input("Post Title", max_chars=200)
        category = st.selectbox("Category", CATEGORIES)
        content = st.text_area("Content", height=200, placeholder="Share your knowledge, ask a question, or start a discussion...")
        submitted = st.form_submit_button("📝 Post", type="primary")

    if submitted:
        if not title.strip() or not content.strip():
            st.error("Please fill in both title and content.")
            return
        execute_query(
            "INSERT INTO community_posts (user_id, title, content, category, created_at) VALUES (%s, %s, %s, %s, %s)",
            (user["id"], title.strip(), content.strip(), category, datetime.now())
        )
        st.success("Post created successfully!")
        st.rerun()


def _show_post_detail(user):
    post_id = st.session_state["view_post_id"]

    if st.button("← Back to Forum"):
        st.session_state["view_post_id"] = None
        st.rerun()

    post = fetch_one(
        "SELECT cp.*, u.name as author_name FROM community_posts cp JOIN users u ON cp.user_id = u.id WHERE cp.id = %s",
        (post_id,)
    )

    if not post:
        st.error("Post not found.")
        st.session_state["view_post_id"] = None
        return

    st.markdown(f"## {post['title']}")
    st.caption(f"By **{post['author_name']}** | {post.get('category', 'General')} | {post['created_at'].strftime('%b %d, %Y %H:%M') if post.get('created_at') else ''}")
    st.markdown(post["content"])
    st.divider()

    st.subheader("💬 Replies")

    replies = fetch_all(
        "SELECT cr.*, u.name as author_name FROM community_replies cr JOIN users u ON cr.user_id = u.id WHERE cr.post_id = %s ORDER BY cr.created_at ASC",
        (post_id,)
    )

    if replies:
        for reply in replies:
            with st.container():
                st.markdown(f"**{reply['author_name']}** — {reply['created_at'].strftime('%b %d, %Y %H:%M') if reply.get('created_at') else ''}")
                st.markdown(reply["content"])
                if reply["user_id"] == user["id"]:
                    if st.button("🗑️", key=f"del_reply_{reply['id']}"):
                        execute_query("DELETE FROM community_replies WHERE id = %s", (reply["id"],))
                        st.rerun()
                st.divider()
    else:
        st.info("No replies yet. Be the first to respond!")

    with st.form("reply_form"):
        reply_content = st.text_area("Write a reply", placeholder="Share your thoughts...")
        reply_submitted = st.form_submit_button("💬 Reply", type="primary")

    if reply_submitted:
        if not reply_content.strip():
            st.error("Please write something before replying.")
            return
        execute_query(
            "INSERT INTO community_replies (post_id, user_id, content, created_at) VALUES (%s, %s, %s, %s)",
            (post_id, user["id"], reply_content.strip(), datetime.now())
        )
        st.success("Reply posted!")
        st.rerun()
