import streamlit as st
import time
import re
import json
import os
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="Cloud YouTube Automation Bot", page_icon="🚀", layout="wide")

REQUESTS_FILE = "pending_requests.json"

# Helper functions to load/save pending requests persistently
def load_pending_requests():
    if os.path.exists(REQUESTS_FILE):
        try:
            with open(REQUESTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_pending_requests(requests_list):
    try:
        with open(REQUESTS_FILE, "w") as f:
            json.dump(requests_list, f)
    except Exception:
        pass

# Initialize session state data
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": "MadaraUchiha786@@!!$$"
    }

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "task_logs" not in st.session_state:
    st.session_state.task_logs = []

if "task_history" not in st.session_state:
    st.session_state.task_history = []

if "validated_url" not in st.session_state:
    st.session_state.validated_url = ""

# Helper function to extract YouTube Video ID for thumbnails
def get_youtube_thumbnail(url):
    pattern = r"(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        vid_id = match.group(1)
        return f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
    return None

# Helper function to check valid YouTube URL
def is_valid_youtube_url(url):
    pattern = r"(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    return bool(re.search(pattern, url))

# Authentication Screen
if not st.session_state.logged_in:
    st.title("🔒 Restricted YouTube Bot Access")
    st.info("🤖 **Bot Assistant:** Welcome! Please log in or request access below.")

    tab1, tab2 = st.tabs(["Login", "Request Access"])
    
    current_pending = load_pending_requests()

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            elif username in [r["username"] for r in current_pending]:
                st.warning("Your request is still pending admin approval.")
            else:
                st.error("Invalid credentials or account not approved yet. Please request access.")
                
    with tab2:
        st.write("New users must request access from the admin before logging in.")
        req_user = st.text_input("Choose a Username to Request", key="req_username")
        req_pass = st.text_input("Choose a Password", type="password", key="req_pass")
        if st.button("Submit Request to Admin"):
            if req_user and req_pass:
                if req_user in st.session_state.users:
                    st.warning("Username already exists.")
                elif req_user in [r["username"] for r in current_pending]:
                    st.warning("Request already pending for this username.")
                else:
                    current_pending.append({"username": req_user, "password": req_pass})
                    save_pending_requests(current_pending)
                    st.success("Request sent successfully! Please wait for the admin to approve it.")
            else:
                st.warning("Please fill in both username and password.")
    st.stop()

# Admin Control Panel Sidebar
if st.session_state.username == "admin":
    st.sidebar.markdown("## 🛡️ Admin Control Panel")
    st.sidebar.subheader("Pending User Approvals")
    
    current_pending = load_pending_requests()
    if len(current_pending) == 0:
        st.sidebar.info("No pending requests.")
    else:
        for idx, req in enumerate(current_pending):
            r_user = req["username"]
            st.sidebar.text(f"User: {r_user}")
            col1, col2 = st.sidebar.columns(2)
            if col1.button(f"Approve", key=f"app_{idx}"):
                st.session_state.users[r_user] = req["password"]
                current_pending.pop(idx)
                save_pending_requests(current_pending)
                st.rerun()
            if col2.button(f"Reject", key=f"rej_{idx}"):
                current_pending.pop(idx)
                save_pending_requests(current_pending)
                st.rerun()
                
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔔 Admin Activity Notifications")
    if len(st.session_state.task_logs) == 0:
        st.sidebar.write("No tasks submitted yet.")
    else:
        for log in reversed(st.session_state.task_logs[-10:]):
            st.sidebar.text(log)

# Main Dashboard App
st.title("🚀 Cloud YouTube Automation Bot")
st.write(f"Logged in as: **{st.session_state.username}**")

if st.button("Logout"):
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.markdown("---")

# Clean Video Layout with Centered "welcome" Text Overlay
st.markdown("""
    <h2 style='text-align: center; color: #ff4b4b; margin-bottom: 0px;'>✨ welcome ✨</h2>
""", unsafe_allow_html=True)

vid_col1, vid_col2, vid_col3 = st.columns([2, 1.5, 2])
with vid_col2:
    try:
        st.video("welcome.mp4", format="video/mp4", autoplay=True, muted=True)
    except Exception:
        pass

st.markdown("---")

# Navigation Tabs for Dashboard and History Panel
tab_dash, tab_history = st.tabs(["🚀 Automation Dashboard", "📊 Live Task & View History"])

with tab_dash:
    # Speed Notice
    st.info("ℹ️ **Speed Limit Notice:** To comply with safety distribution rules, delivery runs at a rate of **500 views in 1 hour**.")

    # Step 1: URL Input and URL Submit Button
    st.subheader("Step 1: Enter & Submit YouTube URL")
    url_input = st.text_input("YouTube Short / Video URL:")
    submit_url_btn = st.button("Submit URL")

    if submit_url_btn:
        if is_valid_youtube_url(url_input):
            st.session_state.validated_url = url_input
            st.success("URL verified and accepted!")
        else:
            st.session_state.validated_url = ""
            st.error("Invalid YouTube URL! Please check the link.")
            
            audio_html = """
                <audio autoplay>
                    <source src="error.mp3" type="audio/mp3">
                </audio>
            """
            st.markdown(audio_html, unsafe_allow_html=True)

    # Proceed with steps if a valid URL has been submitted
    if st.session_state.validated_url:
        yt_url = st.session_state.validated_url
        
        st.markdown("---")
        st.subheader("Step 2: Preview & Target Information")
        
        thumbnail_url = get_youtube_thumbnail(yt_url)
        col1, col2 = st.columns([1, 2])
        with col1:
            if thumbnail_url:
                st.image(thumbnail_url, caption="Fetched Video Thumbnail", width=250)
        with col2:
            st.markdown(f"**Video Status:** Ready for Processing")
            st.markdown(f"**Estimated Base Duration:** Standard Short / Video Format")

        st.markdown("---")
        st.subheader("Step 3: Select Desired Views")
        desired_views = st.number_input("How many views do you want?", min_value=50, max_value=50000, value=500, step=50)

        # Calculate duration dynamically (500 views = 60 mins)
        total_minutes = int((desired_views / 500) * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        duration_str = f"{hours} hour(s) {minutes} minute(s)" if hours > 0 else f"{minutes} minute(s)"

        # PKT Timezone (UTC + 5)
        pkt_zone = timezone(timedelta(hours=5))
        current_pkt_time = datetime.now(pkt_zone)
        completion_time = current_pkt_time + timedelta(minutes=total_minutes)

        st.markdown(f"**Estimated Total Duration:** {duration_str}")
        st.markdown(f"**Expected Completion Time (PKT):** {completion_time.strftime('%I:%M %p, %d %b %Y')}")

        st.markdown("---")
        if st.button("Step 4: Start Task & Run Live Views"):
            import random
            before_views = random.randint(100, 500)
            
            history_record = {
                "user": st.session_state.username,
                "url": yt_url,
                "before": before_views,
                "target": desired_views,
                "current": before_views,
                "status": "In Progress",
                "time": current_pkt_time.strftime('%I:%M %p, %d %b')
            }
            st.session_state.task_history.append(history_record)
            record_index = len(st.session_state.task_history) - 1

            submission_msg = f"[{st.session_state.username}] Target: {desired_views} views for {yt_url}"
            st.session_state.task_logs.append(submission_msg)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            live_views_display = st.empty()
            
            simulation_steps = 20
            step_increment = max(1, desired_views // simulation_steps)
            current_simulated_views = 0
            
            for i in range(simulation_steps + 1):
                current_simulated_views = min(desired_views, i * step_increment)
                progress_percent = int((current_simulated_views / desired_views) * 100)
                
                st.session_state.task_history[record_index]["current"] = before_views + current_simulated_views
                
                progress_bar.progress(progress_percent)
                status_text.text(f"Processing in cloud... Rate: 500 views / hour")
                live_views_display.markdown(f"### 📈 Live Delivered Views: **{before_views + current_simulated_views}** (Started from: {before_views})")
                time.sleep(0.15)
                
            st.session_state.task_history[record_index]["status"] = "Completed ✅"
            completion_msg = f"[DONE] Task processed successfully for: {yt_url}"
            st.session_state.task_logs.append(completion_msg)
            
            st.success(f"Task successfully completed! All {desired_views} views delivered. Finished at {completion_time.strftime('%I:%M %p')} PKT.")

with tab_history:
    st.subheader("📊 Live Task View Tracking History")
    st.write("Monitor real-time progress, starting views, and increasing target counts for all processed links.")
    
    if len(st.session_state.task_history) == 0:
        st.info("No task history recorded yet. Run a task in the Automation Dashboard to view real-time statistics here.")
    else:
        for idx, item in enumerate(reversed(st.session_state.task_history)):
            with st.container():
                cols = st.columns([1.5, 2, 1, 1, 1.2])
                cols[0].markdown(f"**User:** {item['user']}")
                cols[1].markdown(f"🔗 [Video Link]({item['url']})")
                cols[2].markdown(f"Before: **{item['before']}**")
                cols[3].markdown(f"Current: **{item['current']}**")
                cols[4].markdown(f"Status: **{item['status']}**")
                st.progress(min(1.0, (item['current'] - item['before']) / max(1, item['target'])))
                st.markdown("---")
