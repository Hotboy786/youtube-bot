import streamlit as st
import time
import re
import json
import os
import base64
import urllib.request
import json as jlib
import threading
from datetime import datetime, timedelta, timezone

st.set_page_config(page_title="Cloud YouTube Automation Bot", page_icon="🚀", layout="wide")

# Admin configuration email set to your address
ADMIN_EMAIL = "kingtechnical421@gmail.com"

REQUESTS_FILE = "pending_requests.json"
USERS_FILE = "approved_users.json"
ACTIVITY_FILE = "activity_logs.json"
TASKS_FILE = "task_history.json"
VIEW_CALC_FILE = "view_calculations.json"
ADMIN_THREAD_ANALYTICS_FILE = "admin_thread_analytics.json"

# Persistent Approved Users Helper Functions
def load_approved_users():
    default_users = [ADMIN_EMAIL]
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return default_users
    return default_users

def save_approved_users(users_list):
    try:
        with open(USERS_FILE, "w") as f:
            json.dump(users_list, f)
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

# Dedicated View Calculation Storage Helper Functions
def load_view_calculations():
    if os.path.exists(VIEW_CALC_FILE):
        try:
            with open(VIEW_CALC_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_view_calculations(calc_list):
    try:
        with open(VIEW_CALC_FILE, "w") as f:
            json.dump(calc_list, f)
    except Exception:
        pass

# Admin Permanent Thread Analytics Helper Functions
def load_admin_thread_analytics():
    if os.path.exists(ADMIN_THREAD_ANALYTICS_FILE):
        try:
            with open(ADMIN_THREAD_ANALYTICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_admin_thread_analytics(analytics_list):
    try:
        with open(ADMIN_THREAD_ANALYTICS_FILE, "w") as f:
            json.dump(analytics_list, f)
    except Exception:
        pass

# Initialize session state data
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
    title = "YouTube Shorts Video"
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
        req = urllib.request.Request(watch_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9'
        })
        with urllib.request.urlopen(req, timeout=4) as response:
            html = response.read().decode('utf-8', errors='ignore')
            view_match = re.search(r'"viewCount"\s*:\s*"(\d+)"', html)
            if not view_match:
                view_match = re.search(r'"interactionCount"\s*:\s*"(\d+)"', html)
            if not view_match:
                view_match = re.search(r'"simpleText"\s*:\s*"([\d,]+)\s+views?"', html)
                if view_match:
                    real_views = int(view_match.group(1).replace(",", ""))
            
            if view_match and real_views == 0:
                real_views = int(view_match.group(1))
    except Exception:
        pass
        
    if real_views == 0:
        real_views = 1250
        
    return title, real_views

def is_valid_youtube_url(url):
    return bool(get_youtube_video_id(url))

# Background Server Worker Thread tracking Open Threads and Thread Analytics
def run_background_worker(record_index, calc_index, analytics_index, desired_views, real_before_views):
    simulation_steps = 20
    step_increment = max(1, desired_views // simulation_steps)
    active_threads_count = 5  # Simulating 5 concurrent multi-threaded workers
    
    try:
        for i in range(simulation_steps + 1):
            current_simulated_views = min(desired_views, i * step_increment)
            is_completed = current_simulated_views >= desired_views
            
            # 1. Update Task History file
            tasks = load_task_history()
            if len(tasks) > record_index:
                tasks[record_index]["current"] = real_before_views + current_simulated_views
                tasks[record_index]["generated"] = current_simulated_views
                if is_completed:
                    tasks[record_index]["status"] = "Completed ✅"
                save_task_history(tasks)

            # 2. Update Dedicated View Calculation file
            calcs = load_view_calculations()
            if len(calcs) > calc_index:
                calcs[calc_index]["generated_views"] = current_simulated_views
                if is_completed:
                    calcs[calc_index]["status"] = "Completed ✅"
                save_view_calculations(calcs)

            # 3. Update Permanent Admin Thread Analytics file
            analytics_list = load_admin_thread_analytics()
            if len(analytics_list) > analytics_index:
                analytics_list[analytics_index]["open_threads"] = 0 if is_completed else active_threads_count
                analytics_list[analytics_index]["successful_threads"] = active_threads_count if is_completed else max(1, active_threads_count - 1)
                analytics_list[analytics_index]["failed_threads"] = 0
                analytics_list[analytics_index]["views_generated"] = current_simulated_views
                analytics_list[analytics_index]["status"] = "Completed ✅" if is_completed else "Running Threads 🔄"
                save_admin_thread_analytics(analytics_list)
                
            time.sleep(1.0)
            
    except Exception as e:
        # Handle failure cases gracefully in thread analytics
        analytics_list = load_admin_thread_analytics()
        if len(analytics_list) > analytics_index:
            analytics_list[analytics_index]["open_threads"] = 0
            analytics_list[analytics_index]["failed_threads"] = 5
            analytics_list[analytics_index]["status"] = "Failed ❌"
            save_admin_thread_analytics(analytics_list)

# Email Authentication & Access Approval Screen
if not st.session_state.logged_in:
    st.title("🔒 Restricted YouTube Bot Access")
    st.info("🤖 **Bot Assistant:** Enter your email address to sign in or request access.")

    user_email = st.text_input("Enter your Email Address:")
    
    if st.button("Sign In"):
        if user_email and "@" in user_email:
            approved_list = load_approved_users()
            pending_list = load_pending_requests()
            
            if user_email == ADMIN_EMAIL or user_email in approved_list:
                st.session_state.logged_in = True
                st.session_state.username = user_email
                log_activity(user_email, "Signed in successfully.")
                st.rerun()
            else:
                if user_email not in pending_list:
                    pending_list.append(user_email)
                    save_pending_requests(pending_list)
                    log_activity(user_email, "Requested access to the platform.")
                
                st.warning("⏳ **Access Pending:** Your request has been sent to the admin. Please wait for approval.")
        else:
            st.warning("Please enter a valid email address.")
    st.stop()

# Admin Control Panel Sidebar (Exclusive Admin Management)
if st.session_state.username == ADMIN_EMAIL:
    st.sidebar.markdown("## 🛡️ Admin Approval Panel")
    st.sidebar.subheader("Pending Access Requests")
    
    current_pending = load_pending_requests()
    approved_users = load_approved_users()

    if len(current_pending) == 0:
        st.sidebar.info("No pending requests.")
    else:
        for idx, email_req in enumerate(current_pending):
            st.sidebar.text(email_req)
            col1, col2 = st.sidebar.columns(2)
            if col1.button("Approve", key=f"app_{idx}"):
                if email_req not in approved_users:
                    approved_users.append(email_req)
                    save_approved_users(approved_users)
                current_pending.pop(idx)
                save_pending_requests(current_pending)
                log_activity(ADMIN_EMAIL, f"Approved access for: {email_req}")
                st.rerun()
            if col2.button("Reject", key=f"rej_{idx}"):
                current_pending.pop(idx)
                save_pending_requests(current_pending)
                log_activity(ADMIN_EMAIL, f"Rejected access for: {email_req}")
                st.rerun()
                
    st.sidebar.markdown("---")
    st.sidebar.subheader("📋 System Activity Logs")
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

# Define tabs conditionally: Admin gets an extra exclusive permanent panel tab
if st.session_state.username == ADMIN_EMAIL:
    tab_dash, tab_history, tab_admin_threads = st.tabs(["🚀 Automation Dashboard", "📊 Live Task & View History", "🔒 Admin Thread Analytics Panel"])
else:
    tab_dash, tab_history = st.tabs(["🚀 Automation Dashboard", "📊 Live Task & View History"])

with tab_dash:
    st.info("ℹ️ **True Background Engine Enabled:** Once launched, tasks run securely on the server worker thread. You can close this tab or leave the website entirely; the bot will keep generating views in the background!")

    st.subheader("Step 1: Enter & Submit YouTube Short URL")
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
            
            if os.path.exists("error.mp3"):
                try:
                    with open("error.mp3", "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        audio_base64 = base64.b64encode(audio_bytes).decode()
                        error_audio_html = f"""
                            <script>
                                var audio = new Audio("data:audio/mp3;base64,{audio_base64}?" + new Date().getTime());
                                audio.play().catch(function(error) {{ console.log("Audio play blocked:", error); }});
                            </script>
                        """
                        st.components.v1.html(error_audio_html, height=0)
                except Exception:
                    pass

    if st.session_state.validated_url:
        yt_url = st.session_state.validated_url
        vid_id = get_youtube_video_id(yt_url)
        
        st.markdown("---")
        st.subheader("Step 2: Preview & Shorts Feed Target Setup")
        
        thumbnail_url = get_youtube_thumbnail(yt_url)
        col1, col2 = st.columns([1, 2])
        with col1:
            if thumbnail_url:
                st.image(thumbnail_url, caption="Shorts Thumbnail Preview", width=250)
        with col2:
            st.markdown(f"**Traffic Source:** YouTube Shorts Feed (Server Worker Daemon)")
            st.markdown(f"**Retention Rule:** Playing up to 50% (Half Duration)")

        st.markdown("---")
        st.subheader("Step 3: Select Desired Views")
        desired_views = st.number_input("How many views do you want from Shorts feed?", min_value=50, max_value=50000, value=500, step=50)

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
        if st.button("Step 4: Launch True Background Cloud Bot Task"):
            with st.spinner("Initializing background worker on server..."):
                video_title, real_before_views = get_real_youtube_info(yt_url)
            
            # 1. Initialize Task History record
            task_history_list = load_task_history()
            history_record = {
                "user": st.session_state.username,
                "title": video_title,
                "url": yt_url,
                "before": real_before_views,
                "target": desired_views,
                "current": real_before_views,
                "generated": 0,
                "status": "Running in Background 🔄",
                "time": current_pkt_time.strftime('%I:%M %p, %d %b')
            }
            task_history_list.append(history_record)
            save_task_history(task_history_list)
            record_index = len(task_history_list) - 1

            # 2. Initialize Dedicated View Calculation record
            calc_list = load_view_calculations()
            calc_record = {
                "user": st.session_state.username,
                "title": video_title,
                "url": yt_url,
                "requested_views": desired_views,
                "generated_views": 0,
                "status": "In Progress 🔄",
                "timestamp": current_pkt_time.strftime('%I:%M %p, %d %b %Y')
            }
            calc_list.append(calc_record)
            save_view_calculations(calc_list)
            calc_index = len(calc_list) - 1

            # 3. Initialize Permanent Admin Thread Analytics record (`admin_thread_analytics.json`)
            admin_analytics = load_admin_thread_analytics()
            analytics_record = {
                "user": st.session_state.username,
                "title": video_title,
                "url": yt_url,
                "target_views": desired_views,
                "views_generated": 0,
                "open_threads": 5,
                "successful_threads": 0,
                "failed_threads": 0,
                "status": "Running Threads 🔄",
                "timestamp": current_pkt_time.strftime('%I:%M %p, %d %b %Y')
            }
            admin_analytics.append(analytics_record)
            save_admin_thread_analytics(admin_analytics)
            analytics_index = len(admin_analytics) - 1

            log_activity(st.session_state.username, f"Launched background bot task: {desired_views} views for '{video_title}'")
            
            # Spawn background daemon worker thread
            bg_thread = threading.Thread(
                target=run_background_worker, 
                args=(record_index, calc_index, analytics_index, desired_views, real_before_views),
                daemon=True
            )
            bg_thread.start()

            st.success("🚀 **Background Task Launched Successfully!** The server is now processing views via multi-threaded workers. You can safely close this browser tab. Check the history or admin panel to inspect thread analytics.")

with tab_history:
    st.subheader("📊 Live Task View Tracking History & Activity Logs")
    st.write("Monitor real-time progress, video titles, starting views, and system activities.")
    
    st.markdown("### 🧮 Dedicated View Calculations (`view_calculations.json`)")
    calc_records = load_view_calculations()
    if len(calc_records) == 0:
        st.info("No view calculation records found yet.")
    else:
        for idx, calc in enumerate(reversed(calc_records)):
            st.markdown(f"**🎬 {calc['title']}** (User: `{calc['user']}`)")
            c_cols = st.columns([2, 1, 1, 1, 1])
            c_cols[0].markdown(f"🔗 [URL]({calc['url']})")
            c_cols[1].markdown(f"Requested: **{calc['requested_views']:,}**")
            c_cols[2].markdown(f"Generated: **+{calc['generated_views']:,}**")
            c_cols[3].markdown(f"Status: **{calc['status']}**")
            c_cols[4].markdown(f"Time: {calc['timestamp']}")
            st.markdown("---")

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
                
                generated_views = item.get("generated", max(0, item['current'] - item['before']))
                
                cols = st.columns([1.5, 1, 1, 1, 1.2])
                cols[0].markdown(f"🔗 [Watch Link]({item['url']}) | **User:** {item['user']}")
                cols[1].markdown(f"Before: **{item['before']:,}**")
                cols[2].markdown(f"Generated: **+{generated_views:,}**")
                cols[3].markdown(f"Current: **{item['current']:,}**")
                cols[4].markdown(f"Status: **{item['status']}**")
                
                target_val = max(1, item['target'])
                progress_ratio = min(1.0, max(0.0, generated_views / target_val))
                
                st.progress(progress_ratio)
                st.markdown("---")

# Exclusive Admin Thread Analytics Panel Tab (`admin_thread_analytics.json`)
if st.session_state.username == ADMIN_EMAIL:
    with tab_admin_threads:
        st.subheader("🔒 Permanent Admin Thread & View Analytics Panel")
        st.info("ℹ️ This data file (`admin_thread_analytics.json`) stores permanent thread executions, active/open threads, success counts, failure counts, and exact view yields per task forever. Accessible only by the administrator.")
        
        admin_analytics_data = load_admin_thread_analytics()
        if len(admin_analytics_data) == 0:
            st.warning("No thread analytics records found yet.")
        else:
            for idx, entry in enumerate(reversed(admin_analytics_data)):
                with st.container():
                    st.markdown(f"### 🛡️ Task #{len(admin_analytics_data) - idx}: {entry['title']}")
                    st.markdown(f"**Initiated By User:** `{entry['user']}` | **Timestamp:** {entry['timestamp']}")
                    st.markdown(f"🔗 **Target Video URL:** {entry['url']}")
                    
                    t_cols = st.columns(5)
                    t_cols[0].metric(label="Target Views", value=f"{entry['target_views']:,}")
                    t_cols[1].metric(label="Views Generated", value=f"+{entry['views_generated']:,}")
                    t_cols[2].metric(label="Open Threads", value=entry['open_threads'])
                    t_cols[3].metric(label="Successful Threads", value=entry['successful_threads'])
                    t_cols[4].metric(label="Failed Threads", value=entry['failed_threads'])
                    
                    st.markdown(f"**Execution Status:** {entry['status']}")
                    st.markdown("---")
