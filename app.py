import streamlit as st
import time

st.set_page_config(page_title="Cloud YouTube Automation Bot", page_icon="🚀", layout="wide")

# Initialize session state data
if "users" not in st.session_state:
    st.session_state.users = {
        "admin": "MadaraUchiha786@@!!$$",
        "user1": "MadaraUchiha786@@!!$$",
        "user2": "MadaraUchiha786@@!!$$",
        "user3": "MadaraUchiha786@@!!$$",
        "user4": "MadaraUchiha786@@!!$$",
        "user5": "MadaraUchiha786@@!!$$"
    }

if "pending_requests" not in st.session_state:
    st.session_state.pending_requests = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""

if "task_logs" not in st.session_state:
    st.session_state.task_logs = []

# Authentication Screen with Welcoming Bot Feature
if not st.session_state.logged_in:
    st.title("🔒 Restricted YouTube Bot Access")
    
    # Welcoming Bot Message box
    st.info("🤖 **Bot Assistant:** Hello! Welcome to the website. How may I help you today? Please log in or request access below to get started!")
    
    tab1, tab2 = st.tabs(["Login", "Request Access"])
    
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username in st.session_state.users and st.session_state.users[username] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    with tab2:
        req_user = st.text_input("Choose a Username to Request")
        if st.button("Submit Request"):
            if req_user and req_user not in st.session_state.pending_requests:
                st.session_state.pending_requests.append(req_user)
                st.success("Request sent to admin for approval!")
            else:
                st.warning("Invalid or already requested username.")
    st.stop()

# Admin Control Panel Sidebar
if st.session_state.username == "admin":
    st.sidebar.markdown("## 🛡️ Admin Control Panel")
    st.sidebar.subheader("Pending User Requests")
    
    if len(st.session_state.pending_requests) == 0:
        st.sidebar.info("No pending requests.")
    else:
        for req in st.session_state.pending_requests:
            col1, col2 = st.sidebar.columns(2)
            if col1.button(f"Approve {req}", key=f"app_{req}"):
                st.session_state.users[req] = "MadaraUchiha786@@!!$$"
                st.session_state.pending_requests.remove(req)
                st.rerun()
            if col2.button(f"Reject {req}", key=f"rej_{req}"):
                st.session_state.pending_requests.remove(req)
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
yt_url = st.text_input("YouTube Short / Video URL:")

if st.button("Start Task"):
    if yt_url:
        submission_msg = f"[{st.session_state.username}] Submitted: {yt_url}"
        st.session_state.task_logs.append(submission_msg)
        
        with st.spinner("Processing task in the cloud... Please wait."):
            time.sleep(3)
            
        completion_msg = f"[DONE] Task completed for: {yt_url}"
        st.session_state.task_logs.append(completion_msg)
        
        st.success(f"Task successfully completed for {yt_url}!")
    else:
        st.warning("Please enter a valid YouTube URL.")
