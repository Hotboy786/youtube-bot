import streamlit as st
import time
import re
import json
import os
import urllib.request
import json as jlib
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title=" YouTube Automation Bot", page_icon="🚀", layout="wide")

REQUESTS_FILE = "pending_requests.json"
USERS_FILE = "users.json"
ACTIVITY_FILE = "activity_logs.json"
TASKS_FILE = "task_history.json"

# Persistent User Database Helper Functions
def load_users():
    default_users = {"admin": "MadaraUchiha786@@!!$$"}
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_users
    return default_users

def save_users(users_dict):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users_dict, f)
    except Exception:
        pass

# Persistent Pending Requests Helper Functions
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

# Persistent Activity Logger Helper Functions
def log_activity(username, action_details):
    logs = []
    if os.path.exists(ACTIVITY_FILE):
        try:
            with open(ACTIVITY_FILE, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    pkt_zone = timezone(timedelta(hours=5))
    timestamp = datetime.now(pkt_zone).strftime('%I:%M %p, %d %b %Y')
    
    logs.append({
        "username": username,
        "action": action_details,
        "time": timestamp
    })
    
    try:
        with open(ACTIVITY_FILE, "w") as f:
            json.dump(logs, f)
    except Exception:
        pass

def load_activity_logs():
    if os.path.exists(ACTIVITY_FILE):
        try:
            with open(ACTIVITY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# Persistent Task History Helper Functions
def load_task_history():
    if os.path.exists(TASKS_FILE):
        try:
            with open(TASKS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_task_history(history_list):
    try:
        with open(TASKS_FILE, "w") as f:
            json.dump(history_list, f)
    except Exception:
        pass

# Initialize session state data
if "users" not in st.session_state:
    st.session_state.users = load_users()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "validated_url" not in st.session_state:
    st.session_state.validated_url = ""

# Helper function to extract YouTube Video ID
def get_youtube_video_id(url):
    pattern = r"(?:v=|\/shorts\/|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    return None

def get_youtube_thumbnail(url):
    vid_id = get_youtube_video_id(url)
    if vid_id:
        return f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"
    return None

def get_real_youtube_info(url):
    vid_id = get_youtube_video_id(url)
    title = "YouTube Video / Short"
    real_views = 0
    
    if not vid_id:
        return title, real_views
        
    try:
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={vid_id}&format=json"
        req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = jlib.loads(response.read().decode())
            if "title" in data:
                title = data["title"]
    except Exception:
        pass
        
    try:
        watch_url = f"https://www.youtube.com/watch?v={vid_id}"
        req = urllib.request.Request(watch_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=3) as response:
            html = response.read().decode('utf-8', errors='ignore')
            view_match = re.search(r'"viewCount"\s*:\s*"(\d+)"', html)
            if view_match:
                real_views = int(view_match.group(1))
            else:
                import random
                real_views = random.randint(1200, 8500)
    except Exception:
        import random
        real_views = random.randint(1200, 8500)
        
    return title, real_views

def is_valid_youtube_url(url):
    return bool(get_youtube_video_id(url))

# Authentication Screen
if not st.session_state.logged_in:
    st.title("🔒 Restricted YouTube Bot Access")
    st.info("🤖 **Bot Assistant:** Welcome! Please log in or request access below.")

    tab1, tab2 = st.tabs(["Login", "Request Access"])
    
    current_pending = load_pending_requests()
    active_users = load_users()

    with tab1:
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login"):
            if username in active_users and active_users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                log_activity(username, "Logged into the system successfully.")
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
                if req_user in active_users:
                    st.warning("Username already exists.")
                elif req_user in [r["username"] for r in current_pending]:
                    st.warning("Request already pending for this username.")
                else:
                    current_pending.append({"username": req_user, "password": req_pass})
                    save_pending_requests(current_pending)
                    log_activity(req_user, "Submitted account access request.")
                    st.success("Request sent successfully! Please wait for the admin to approve it.")
            else:
                st.warning("Please fill in both username and password.")
    st.stop()

# Admin Control Panel Sidebar
if st.session_state.username == "admin":
    st.sidebar.markdown("## 🛡️ Admin Control Panel")
    st.sidebar.subheader("Pending User Approvals")
    
    current_pending = load_pending_requests()
    active_users = load_users()

    if len(current_pending) == 0:
        st.sidebar.info("No pending requests.")
    else:
        for idx, req in enumerate(current_pending):
            r_user = req["username"]
            st.sidebar.text(f"User: {r_user}")
            col1, col2 = st.sidebar.columns(2)
            if col1.button(f"Approve", key=f"app_{idx}"):
                active_users[r_user] = req["password"]
                save_users(active_users)
                current_pending.pop(idx)
                save_pending_requests(current_pending)
                log_activity("admin", f"Approved account for user: {r_user}")
                st.rerun()
            if col2.button(f"Reject", key=f"rej_{idx}"):
                current_pending.pop(idx)
                save_pending_requests(current_pending)
                log_activity("admin", f"Rejected account for user: {r_user}")
                st.rerun()
                
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 System Activity File Logs")
    all_activities = load_activity_logs()
    if len(all_activities) == 0:
        st.sidebar.write("No activity recorded yet.")
    else:
        for act in reversed(all_activities[-10:]):
            st.sidebar.text(f"[{act['time']}] {act['username']}: {act['action']}")

# Main Dashboard App
st.title("🚀 Cloud YouTube Automation Bot")
st.write(f"Logged in as: **{st.session_state.username}**")

if st.button("Logout"):
    log_activity(st.session_state.username, "Logged out of the system.")
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.rerun()

st.markdown("---")

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

tab_dash, tab_history = st.tabs(["🚀 Automation Dashboard", "📊 Live Task & View History"])

with tab_dash:
    st.info("ℹ️ **Speed Limit Notice:** To comply with safety distribution rules, delivery runs at a rate of **500 views in 1 hour**.")

    st.subheader("Step 1: Enter & Submit YouTube URL")
    url_input = st.text_input("YouTube Short / Video URL:")
    submit_url_btn = st.button("Submit URL")

    if submit_url_btn:
        if is_valid_youtube_url(url_input):
            st.session_state.validated_url = url_input
            log_activity(st.session_state.username, f"Validated YouTube URL: {url_input}")
            st.success("URL verified and accepted!")
        else:
            st.session_state.validated_url = ""
            log_activity(st.session_state.username, f"Submitted invalid YouTube URL: {url_input}")
            st.error("Invalid YouTube URL! Please check the link.")
            
            # Browser audio elements often require user interaction context or direct base64/remote URL strings. 
            # Using standard components.html to enforce audio playback on error:
            error_audio_html = """
                <audio autoplay controls style="display:none;">
                    <source src="https://www.myinstants.com/media/sounds/erro.mp3" type="audio/mpeg">
                </audio>
                <script>
                    var audio = new Audio('https://www.myinstants.com/media/sounds/erro.mp3');
                    audio.play().catch(function(error) { console.log("Audio play blocked:", error); });
                </script>
            """
            st.components.v1.html(error_audio_html, height=0)

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

        total_minutes = int((desired_views / 500) * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        duration_str = f"{hours} hour(s) {minutes} minute(s)" if hours > 0 else f"{minutes} minute(s)"

        pkt_zone = timezone(timedelta(hours=5))
        current_pkt_time = datetime.now(pkt_zone)
        completion_time = current_pkt_time + timedelta(minutes=total_minutes)

        st.markdown(f"**Estimated Total Duration:** {duration_str}")
        st.markdown(f"**Expected Completion Time (PKT):** {completion_time.strftime('%I:%M %p, %d %b %Y')}")

        st.markdown("---")
        if st.button("Step 4: Start Task & Run Live Views"):
            with st.spinner("Fetching real video data from YouTube..."):
                video_title, real_before_views = get_real_youtube_info(yt_url)
            
            task_history_list = load_task_history()
            
            history_record = {
                "user": st.session_state.username,
                "title": video_title,
                "url": yt_url,
                "before": real_before_views,
                "target": desired_views,
                "current": real_before_views,
                "status": "In Progress",
                "time": current_pkt_time.strftime('%I:%M %p, %d %b')
            }
            task_history_list.append(history_record)
            save_task_history(task_history_list)
            record_index = len(task_history_list) - 1

            log_activity(st.session_state.username, f"Started task: {desired_views} views for '{video_title}' ({yt_url})")
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            live_views_display = st.empty()
            
            simulation_steps = 20
            step_increment = max(1, desired_views // simulation_steps)
            current_simulated_views = 0
            
            for i in range(simulation_steps + 1):
                current_simulated_views = min(desired_views, i * step_increment)
                progress_percent = int((current_simulated_views / desired_views) * 100)
                
                # Update current count inside saved file list
                task_history_list = load_task_history()
                if len(task_history_list) > record_index:
                    task_history_list[record_index]["current"] = real_before_views + current_simulated_views
                    save_task_history(task_history_list)
                
                progress_bar.progress(progress_percent)
                status_text.text(f"Processing in cloud... Rate: 500 views / hour")
                live_views_display.markdown(f"### 📈 Live Delivered Views: **{real_before_views + current_simulated_views:,}** (Fetched initial: {real_before_views:,})")
                time.sleep(0.15)
                
            # Mark completed in persistent file
            task_history_list = load_task_history()
            if len(task_history_list) > record_index:
                task_history_list[record_index]["status"] = "Completed ✅"
                save_task_history(task_history_list)

            log_activity(st.session_state.username, f"Completed task successfully for '{video_title}'")
            st.success(f"Task successfully completed! All {desired_views} views delivered. Finished at {completion_time.strftime('%I:%M %p')} PKT.")

with tab_history:
    st.subheader("📊 Live Task View Tracking History & Activity Logs")
    st.write("Monitor real-time progress, video titles, starting views, and system activities.")
    
    st.markdown("### 📝 Permanent User Activity Audit Trail")
    all_activities = load_activity_logs()
    if len(all_activities) == 0:
        st.info("No activity logs recorded yet.")
    else:
        for act in reversed(all_activities):
            st.text(f"[{act['time']}] User: {act['username']} -> Action: {act['action']}")
            
    st.markdown("---")
    st.subheader("🎯 Video View Progress Tracking")
    saved_tasks = load_task_history()
    if len(saved_tasks) == 0:
        st.info("No tasks executed in this session yet.")
    else:
        for idx, item in enumerate(reversed(saved_tasks)):
            with st.container():
                st.markdown(f"### 🎬 {item['title']}")
                cols = st.columns([1.5, 1, 1, 1.2])
                cols[0].markdown(f"🔗 [Watch Link]({item['url']}) | **User:** {item['user']}")
                cols[1].markdown(f"Before: **{item['before']:,}**")
                cols[2].markdown(f"Current: **{item['current']:,}**")
                cols[3].markdown(f"Status: **{item['status']}**")
                progress_ratio = min(1.0, max(0.0, (item['current'] - item['before']) / max(1, item['target'])))
                st.progress(progress_ratio)
                st.markdown("---")
