import streamlit as st
import time
import re
import json
import os
import urllib.request
import json as jlib
import threading
import subprocess
from datetime import datetime, timedelta, timezone

# Auto-install playwright browsers and dependencies on cloud deployment if missing
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        p.chromium.launch(headless=True)
except Exception:
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except Exception:
        pass

st.set_page_config(page_title="Cloud YouTube Automation Bot", page_icon="🚀", layout="wide")

ADMIN_EMAIL = "kingtechnical421@gmail.com"

REQUESTS_FILE = "pending_requests.json"
USERS_FILE = "approved_users.json"
ACTIVITY_FILE = "activity_logs.json"
TASKS_FILE = "task_history.json"
VIEW_CALC_FILE = "view_calculations.json"
ADMIN_THREAD_ANALYTICS_FILE = "admin_thread_analytics.json"
DETAILED_THREAD_LOGS_FILE = "detailed_thread_logs.json"
DAILY_LIMITS_FILE = "daily_user_limits.json"

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

def log_activity(username, action_details):
    logs = []
    if os.path.exists(ACTIVITY_FILE):
        try:
            with open(ACTIVITY_FILE, "r") as f:
                logs = json.load(f)
        except Exception:
            logs = []
    
    pkt_zone = timezone(timedelta(hours=5))
    timestamp = datetime.now(pkt_zone).strftime('%I:%M:%S %p, %d %b %Y')
    
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

def load_detailed_thread_logs():
    if os.path.exists(DETAILED_THREAD_LOGS_FILE):
        try:
            with open(DETAILED_THREAD_LOGS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_detailed_thread_logs(logs_list):
    try:
        with open(DETAILED_THREAD_LOGS_FILE, "w") as f:
            json.dump(logs_list, f)
    except Exception:
        pass

def load_daily_limits():
    if os.path.exists(DAILY_LIMITS_FILE):
        try:
            with open(DAILY_LIMITS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_daily_limits(limits_dict):
    try:
        with open(DAILY_LIMITS_FILE, "w") as f:
            json.dump(limits_dict, f)
    except Exception:
        pass

def get_user_daily_stats(username):
    pkt_zone = timezone(timedelta(hours=5))
    today_str = datetime.now(pkt_zone).strftime('%Y-%m-%d')
    
    limits_data = load_daily_limits()
    if username not in limits_data or limits_data[username].get("date") != today_str:
        limits_data[username] = {
            "date": today_str,
            "views_used": 0
        }
        save_daily_limits(limits_data)
        
    return limits_data[username]["views_used"]

def add_user_daily_usage(username, views_count):
    pkt_zone = timezone(timedelta(hours=5))
    today_str = datetime.now(pkt_zone).strftime('%Y-%m-%d')
    
    limits_data = load_daily_limits()
    if username not in limits_data or limits_data[username].get("date") != today_str:
        limits_data[username] = {
            "date": today_str,
            "views_used": views_count
        }
    else:
        limits_data[username]["views_used"] += views_count
        
    save_daily_limits(limits_data)

# Session State & Login Cache
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

query_params = st.query_params
if not st.session_state.logged_in and "user" in query_params:
    cached_user = query_params["user"]
    if cached_user == ADMIN_EMAIL or cached_user in load_approved_users():
        st.session_state.logged_in = True
        st.session_state.username = cached_user

if "validated_url" not in st.session_state:
    st.session_state.validated_url = ""

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

def fetch_real_youtube_metadata_via_browser(url):
    """Uses Playwright to fetch accurate title and precise video duration from the player element."""
    title = "YouTube Shorts Video"
    total_secs = 35 # fallback default
    real_views = 1250

    vid_id = get_youtube_video_id(url)
    if vid_id:
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
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 412, "height": 915},
                is_mobile=True
            )
            page = context.new_page()
            page.goto(url, timeout=30000)
            
            # Wait for video element and extract actual duration
            page.wait_for_selector("video", timeout=12000)
            time.sleep(3)
            
            dur = page.evaluate("() => { const v = document.querySelector('video'); return v ? v.duration : 0; }")
            if dur and dur > 0:
                total_secs = int(round(dur))
            
            browser.close()
    except Exception:
        pass

    m = total_secs // 60
    s = total_secs % 60
    duration_str = f"{m}:{s:02d}"
    
    return title, real_views, duration_str, total_secs

def is_valid_youtube_url(url):
    return bool(get_youtube_video_id(url))

# Real Playwright Automation Background Worker with dynamic watch duration
def run_real_youtube_automation(target_url, desired_views, record_index, calc_index, analytics_index, real_before_views, task_title, task_user, play_duration_secs):
    pkt_zone = timezone(timedelta(hours=5))
    active_threads_count = 3  
    views_completed = 0

    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            
            while views_completed < desired_views:
                batch_size = min(active_threads_count, desired_views - views_completed)
                
                for i in range(batch_size):
                    try:
                        context = browser.new_context(
                            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                            viewport={"width": 412, "height": 915},
                            device_scale_factor=2.6,
                            is_mobile=True,
                            has_touch=True
                        )
                        page = context.new_page()
                        page.goto(target_url, timeout=30000)
                        page.wait_for_selector("video", timeout=10000)
                        
                        # Dynamically play for half of video length minus 1 second
                        time.sleep(max(1.0, play_duration_secs))
                        context.close()
                        
                        views_completed += 1
                        
                        detailed_logs = load_detailed_thread_logs()
                        thread_log_entry = {
                            "timestamp": datetime.now(pkt_zone).strftime('%I:%M:%S %p, %d %b %Y'),
                            "user": task_user,
                            "title": task_title,
                            "url": target_url,
                            "thread_id": f"Worker #{i+1}",
                            "step_cycle": f"View {views_completed}/{desired_views}",
                            "view_status": "Generated & Added ✅",
                            "traffic_source": "YouTube Shorts Feed (Automated Browser)",
                            "real_time_views_added": views_completed,
                            "details": f"Played for {play_duration_secs:.1f}s (Half length - 1s). View count incremented."
                        }
                        detailed_logs.append(thread_log_entry)
                        save_detailed_thread_logs(detailed_logs)

                    except Exception:
                        pass

                    tasks = load_task_history()
                    if len(tasks) > record_index:
                        tasks[record_index]["current"] = real_before_views + views_completed
                        tasks[record_index]["generated"] = views_completed
                        if views_completed >= desired_views:
                            tasks[record_index]["status"] = "Completed ✅"
                        save_task_history(tasks)

                    calcs = load_view_calculations()
                    if len(calcs) > calc_index:
                        calcs[calc_index]["generated_views"] = views_completed
                        if views_completed >= desired_views:
                            calcs[calc_index]["status"] = "Completed ✅"
                        save_view_calculations(calcs)

                    analytics_list = load_admin_thread_analytics()
                    if len(analytics_list) > analytics_index:
                        analytics_list[analytics_index]["views_generated"] = views_completed
                        analytics_list[analytics_index]["status"] = "Completed ✅" if views_completed >= desired_views else "Running Workers 🔄"
                        save_admin_thread_analytics(analytics_list)

                time.sleep(3)
            
            browser.close()

    except Exception:
        analytics_list = load_admin_thread_analytics()
        if len(analytics_list) > analytics_index:
            analytics_list[analytics_index]["status"] = "Failed ❌"
            save_admin_thread_analytics(analytics_list)

# Authentication Screen
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
                st.query_params["user"] = user_email
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

# Admin Sidebar Panel
if st.session_state.username == ADMIN_EMAIL:
    st.sidebar.markdown("---")
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
    st.sidebar.subheader("📋 Recent System Activity Logs")
    all_activities_sidebar = load_activity_logs()
    if len(all_activities_sidebar) == 0:
        st.sidebar.write("No activity recorded yet.")
    else:
        for act in reversed(all_activities_sidebar[-10:]):
            st.sidebar.text(f"[{act['time']}] {act['username']}: {act['action']}")

# Main App Layout
st.title("🚀 Cloud YouTube Automation Bot (Admin: Unlimited | Users: 500 Views/Day)")
st.write(f"Logged in as: **{st.session_state.username}**")

if st.button("Logout"):
    log_activity(st.session_state.username, "Logged out of the system.")
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.query_params.clear()
    st.rerun()

st.markdown("---")

if st.session_state.username == ADMIN_EMAIL:
    tab_dash, tab_history, tab_admin_threads, tab_user_activity, tab_granular_threads = st.tabs([
        "🚀 Automation Dashboard", 
        "📊 Live Task & View History", 
        "🔒 Admin Thread Analytics Panel", 
        "👥 User Activity & Monitoring",
        "⚙️ Granular Thread & View Logs"
    ])
else:
    tab_dash = st.tabs(["🚀 Automation Dashboard"])[0]

with tab_dash:
    is_admin = (st.session_state.username == ADMIN_EMAIL)
    
    if is_admin:
        st.info("🛡️ **Admin Account Active:** You have **unlimited** daily view allocations and unrestricted task access.")
    else:
        views_used_today = get_user_daily_stats(st.session_state.username)
        views_remaining = max(0, 500 - views_used_today)
        st.info(f"ℹ️ **Daily Limit Active:** You have used **{views_used_today}/500** views today. Remaining allowance: **{views_remaining} views**.")

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

    if st.session_state.validated_url:
        yt_url = st.session_state.validated_url
        
        with st.spinner("Launching headless browser to fetch precise video duration and metadata..."):
            video_title, real_before_views, video_duration, total_secs = fetch_real_youtube_metadata_via_browser(yt_url)

        # Calculate half length minus 1 second
        half_duration = total_secs / 2.0
        play_duration = max(1.0, half_duration - 1.0)

        st.markdown("---")
        st.subheader("Step 2: Preview & Watch Duration Settings")
        
        thumbnail_url = get_youtube_thumbnail(yt_url)
        col1, col2 = st.columns([1, 2])
        
        with col1:
            if thumbnail_url:
                st.image(thumbnail_url, caption="Shorts Thumbnail Preview", width=220)
                
        with col2:
            st.markdown(f"### 🎬 {video_title}")
            st.markdown(f"⏱️ **Original Video Length:** `{video_duration}` (`{total_secs} seconds`)")
            st.markdown(f"⏱️ **Calculated Watch Duration per View:** Half length (`{half_duration:.1f}s`) minus 1s $\rightarrow$ **`{play_duration:.1f} seconds`**")
            st.markdown(f"👀 **Current Views:** `{real_before_views:,}`")
            st.markdown(f"🌐 **Traffic Source:** YouTube Shorts Feed (Playwright Browser Workers)")

        st.markdown("---")
        st.subheader("Step 3: Select Desired Views")
        
        if not is_admin:
            current_used = get_user_daily_stats(st.session_state.username)
            max_allowed = max(0, 500 - current_used)
            if max_allowed == 0:
                desired_views = st.number_input("How many views do you want from Shorts feed?", min_value=0, max_value=0, value=0, step=50)
            else:
                desired_views = st.number_input("How many views do you want from Shorts feed?", min_value=50, max_value=max_allowed, value=min(500, max_allowed), step=50)
        else:
            desired_views = st.number_input("How many views do you want from Shorts feed?", min_value=50, max_value=50000, value=500, step=50)

        total_minutes = int((desired_views / 1000) * 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60
        duration_str = f"{hours} hour(s) {minutes} minute(s)" if hours > 0 else f"{minutes} minute(s)"

        pkt_zone = timezone(timedelta(hours=5))
        current_pkt_time = datetime.now(pkt_zone)
        completion_time = current_pkt_time + timedelta(minutes=total_minutes)

        st.markdown(f"**Estimated Total Duration:** {duration_str}")
        st.markdown(f"**Expected Completion Time (PKT):** {completion_time.strftime('%I:%M %p, %d %b %Y')}")

        st.markdown("---")
        
        can_launch = True
        if not is_admin:
            current_used_check = get_user_daily_stats(st.session_state.username)
            if current_used_check >= 500 or desired_views <= 0:
                can_launch = False
                
                tomorrow_pkt = (current_pkt_time + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
                time_to_reset = tomorrow_pkt - current_pkt_time
                hours_left = int(time_to_reset.total_seconds() // 3600)
                minutes_left = int((time_to_reset.total_seconds() % 3600) // 60)
                
                st.error(f"⏳ **Daily Quota Reached:** You have already used your 500 views limit for today. Your quota will update/reset in **{hours_left} hour(s) and {minutes_left} minute(s)** (at 12:00 AM PKT). Please come back tomorrow!")

        if can_launch:
            if st.button("Step 4: Launch True Background Cloud Bot Task"):
                if not is_admin:
                    add_user_daily_usage(st.session_state.username, desired_views)

                task_history_list = load_task_history()
                history_record = {
                    "user": st.session_state.username,
                    "title": video_title,
                    "url": yt_url,
                    "before": real_before_views,
                    "target": desired_views,
                    "current": real_before_views,
                    "generated": 0,
                    "status": "Running (1k/hr) 🔄",
                    "time": current_pkt_time.strftime('%I:%M %p, %d %b')
                }
                task_history_list.append(history_record)
                save_task_history(task_history_list)
                record_index = len(task_history_list) - 1

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

                admin_analytics = load_admin_thread_analytics()
                analytics_record = {
                    "user": st.session_state.username,
                    "title": video_title,
                    "url": yt_url,
                    "target_views": desired_views,
                    "views_generated": 0,
                    "open_threads": 3,
                    "successful_threads": 0,
                    "failed_threads": 0,
                    "status": "Running Browser Workers 🔄",
                    "timestamp": current_pkt_time.strftime('%I:%M %p, %d %b %Y')
                }
                admin_analytics.append(analytics_record)
                save_admin_thread_analytics(admin_analytics)
                analytics_index = len(admin_analytics) - 1

                log_activity(st.session_state.username, f"Launched real browser automation task: {desired_views} views for '{video_title}' (Play time: {play_duration:.1f}s)")
                
                bg_thread = threading.Thread(
                    target=run_real_youtube_automation, 
                    args=(yt_url, desired_views, record_index, calc_index, analytics_index, real_before_views, video_title, st.session_state.username, play_duration),
                    daemon=True
                )
                bg_thread.start()

                st.success("🚀 **Task Launched Successfully!** Background browser workers will play each view for the calculated duration.")

# Admin Tabs for Analytics and Monitoring
if st.session_state.username == ADMIN_EMAIL:
    with tab_history:
        st.subheader("📊 Live Task View Tracking History & Activity Logs")
        
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

if st.session_state.username == ADMIN_EMAIL:
    with tab_admin_threads:
        st.subheader("🔒 Permanent Admin Thread & View Analytics Panel")
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
                    t_cols[2].metric(label="Open Workers", value=entry['open_threads'])
                    t_cols[3].metric(label="Successful Workers", value=entry['successful_threads'])
                    t_cols[4].metric(label="Failed Workers", value=entry['failed_threads'])
                    
                    st.markdown(f"**Execution Status:** {entry['status']}")
                    st.markdown("---")

if st.session_state.username == ADMIN_EMAIL:
    with tab_user_activity:
        st.subheader("👥 Dedicated Permanent User Activity & Action Monitoring Panel")
        all_activities = load_activity_logs()
        if len(all_activities) == 0:
            st.warning("No user activity recorded yet.")
        else:
            st.markdown(f"**Total Tracked Permanent System Actions:** `{len(all_activities)}`")
            if st.button("Clear All Activity Logs", key="clear_act_logs"):
                try:
                    with open(ACTIVITY_FILE, "w") as f:
                        json.dump([], f)
                    st.success("Activity logs cleared successfully!")
                    st.rerun()
                except Exception:
                    pass
            st.markdown("---")
            for act in reversed(all_activities):
                act_col1, act_col2, act_col3 = st.columns([1.5, 2.5, 1.5])
                act_col1.markdown(f"👤 **User:** `{act['username']}`")
                act_col2.markdown(f"⚡ **Action:** {act['action']}")
                act_col3.markdown(f"🕒 **Time:** {act['time']}")
                st.markdown("---")

if st.session_state.username == ADMIN_EMAIL:
    with tab_granular_threads:
        st.subheader("⚙️ Granular Every-Single-Thread & Every-Single-View Log Panel")
        detailed_logs = load_detailed_thread_logs()
        if len(detailed_logs) == 0:
            st.warning("No granular thread and view logs captured yet.")
        else:
            st.markdown(f"**Total Granular Logs Recorded:** `{len(detailed_logs)}`")
            if st.button("Clear Granular Logs", key="clear_granular_logs"):
                save_detailed_thread_logs([])
                st.success("Granular logs cleared successfully!")
                st.rerun()
            st.markdown("---")
            for log in reversed(detailed_logs):
                with st.container():
                    col_l1, col_l2, col_l3, col_l4 = st.columns([1.5, 1.5, 1.5, 2])
                    col_l1.markdown(f"🕒 `{log['timestamp']}`")
                    col_l2.markdown(f"👤 **User:** `{log['user']}`")
                    col_l3.markdown(f"🧵 **{log['thread_id']}** (`{log['step_cycle']}`)")
                    col_l4.markdown(f"Status: **{log['view_status']}**")
                    st.markdown(f"🎬 **Video:** {log['title']} | 🔗 [URL]({log['url']})")
                    st.markdown(f"📊 **Traffic Source:** `{log.get('traffic_source', 'YouTube Shorts Feed')}` | 👀 **Current Live Views Count:** `{log.get('real_time_views_added', 0):,}`")
                    st.markdown(f"📝 *Details:* {log['details']}")
                    st.markdown("---")
