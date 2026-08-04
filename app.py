import streamlit as st
import time
import random
import re
import yt_dlp
from selenium import webdriver
from selenium.webdriver.common.by import By

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Cloud YouTube Bot with Admin Approval", page_icon="🤖", layout="centered")

# --- INITIALIZE DATABASE STATES IN CLOUD SESSION ---
if "approved_users" not in st.session_state:
    # 5 Initial user slots pre-configured with your exact password
    st.session_state.approved_users = {
        "user1": "MadaraUchiha786@@!!$$",
        "user2": "MadaraUchiha786@@!!$$",
        "user3": "MadaraUchiha786@@!!$$",
        "user4": "MadaraUchiha786@@!!$$",
        "user5": "MadaraUchiha786@@!!$$",
        "admin": "MadaraUchiha786@@!!$$"  # Master Admin account
    }

if "pending_requests" not in st.session_state:
    st.session_state.pending_requests = []

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = ""

# --- LOGIN & PERMISSION GATEKEEPER SYSTEM ---
def check_login():
    if not st.session_state.authenticated:
        st.title("🔒 Restricted YouTube Bot Access")
        st.write("Please log in. If you are a new user, you will need to request admin permission.")
        
        tab1, tab2 = st.tabs(["Login", "Request Access"])
        
        with tab1:
            username = st.text_input("Username", key="login_user")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Login"):
                if username in st.session_state.approved_users:
                    if st.session_state.approved_users[username] == password:
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect password!")
                else:
                    st.error("Username not found or not approved yet. Please use the 'Request Access' tab.")
                    
        with tab2:
            st.write("Send a notification request to the Admin for link access.")
            new_user_req = st.text_input("Choose a Username to Request", key="req_user")
            if st.button("Submit Request to Admin"):
                if new_user_req:
                    if new_user_req not in st.session_state.pending_requests and new_user_req not in st.session_state.approved_users:
                        st.session_state.pending_requests.append(new_user_req)
                        st.success("Request sent successfully! Ask the Admin to approve you.")
                    else:
                        st.warning("This username is already pending or already exists.")
                else:
                    st.error("Please type a valid username.")
        return False
    return True

if not check_login():
    st.stop()

# --- ADMIN PANEL (Visible only if logged in as 'admin') ---
if st.session_state.username == "admin":
    with st.sidebar:
        st.header("🛠️ Admin Control Panel")
        st.write("Manage access requests from users:")
        
        if len(st.session_state.pending_requests) == 0:
            st.info("No pending requests.")
        else:
            for req in st.session_state.pending_requests:
                st.write(f"User: **{req}**")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Approve", key=f"app_{req}"):
                        # Grant access using your universal password requirement
                        st.session_state.approved_users[req] = "MadaraUchiha786@@!!$$"
                        st.session_state.pending_requests.remove(req)
                        st.success(f"Approved {req}!")
                        st.rerun()
                with col_b:
                    if st.button("Reject", key=f"rej_{req}"):
                        st.session_state.pending_requests.remove(req)
                        st.rerun()
        st.markdown("---")

# --- MAIN APP INTERFACE ---
st.title("🚀 Cloud YouTube Automation Bot")
col_top1, col_top2 = st.columns([3, 1])
with col_top1:
    st.write(f"Logged in as: **{st.session_state.username}**")
with col_top2:
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()

st.markdown("---")

def get_youtube_video_id(url):
    regex = r"(?:v=|\/([0-9A-Za-z_-]{11})|youtu\.be\/|\/embed\/|\/v\/|\/shorts\/)([^#\&\?]*)"
    match = re.search(regex, url)
    if match:
        extracted = match.group(1) or match.group(2)
        if len(extracted) == 11:
            return extracted
    return None

def fetch_video_metadata(url):
    ydl_opts = {'quiet': True, 'no_warnings': True, 'skip_download': True}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return info.get('view_count', 0), info.get('duration', 0)
    except Exception:
        return None, 0

# STEP 1: Input URL
url_input = st.text_input("YouTube Short / Video URL:", placeholder="https://www.youtube.com/shorts/...")

if url_input:
    video_id = get_youtube_video_id(url_input)
    if not video_id:
        st.error("Invalid YouTube URL!")
    else:
        st.image(f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg", width=250)
        
        with st.spinner("Fetching video metadata..."):
            initial_views, duration_sec = fetch_video_metadata(url_input)
        
        if initial_views is not None:
            st.info(f"📊 Current Views on YouTube: **{initial_views:,}**")
        
        # STEP 2: Parameters & Smart Rate Limiter Check
        st.markdown("### ⚙️ View Parameters & Rate Limiter")
        col1, col2 = st.columns(2)
        
        with col1:
            total_views = st.number_input("Total Views to Generate", min_value=1, max_value=5000, value=10)
            time_window_mins = st.number_input("Target Time Window (Minutes)", min_value=1, max_value=1440, value=30)
            
        with col2:
            base_duration = st.number_input("Video Duration (Seconds)", value=int(duration_sec) if duration_sec > 0 else 15)
            max_threads = st.slider("Concurrent Threads", 1, 5, 2)

        views_per_minute = total_views / time_window_mins
        if views_per_minute > 20:
            st.warning("⚠️ **Warning:** Rate is too high! (More than 20 views/minute). YouTube might instantly filter these views. Consider increasing your time window.")
        
        if st.button("Start Cloud Automation"):
            st.write("Starting automated queue simulation...")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            delay_per_task = (time_window_mins * 60) / total_views
            
            for i in range(total_views):
                status_text.text(f"Processing task {i+1} of {total_views}...")
                
                try:
                    options = webdriver.FirefoxOptions()
                    options.add_argument("-private")
                    options.add_argument("--headless")
                    options.page_load_strategy = 'none'
                    
                    driver = webdriver.Firefox(options=options)
                    clean_url = url_input.split("&")[0].split("?si=")[0]
                    driver.get(clean_url)
                    time.sleep(base_duration / 2.0)
                    driver.quit()
                    success_count += 1
                except Exception as e:
                    print(f"Error in task: {e}")
                
                progress_bar.progress((i + 1) / total_views)
                
                if i < total_views - 1:
                    time.sleep(min(delay_per_task, 5))
                    
            st.success(f"Automation sequence finished! Successfully processed {success_count}/{total_views} requests.")