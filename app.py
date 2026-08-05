monitor_container = st.container()

        with monitor_container:
            detailed_logs_live = load_detailed_thread_logs()
            user_logs = [l for l in detailed_logs_live if l['user'] == st.session_state.username and l['url'] == yt_url]
            
            if len(user_logs) == 0:
                st.info("ℹ️ No active view generation logs found yet for this URL. Launch the task above to start tracking views live!")
            else:
                st.markdown("#### 📋 Recent View Generation Logs for Current Task:")
                
                # Reverse logs to show newest first, then slice up to desired_views
                relevant_logs = list(reversed(user_logs[-desired_views:]))
                
                # Chunk logs into groups of 10 for pagination tabs
                chunk_size = 10
                log_chunks = [relevant_logs[i:i + chunk_size] for i in range(0, len(relevant_logs), chunk_size)]
                
                # Create tab names dynamically (e.g., Views 1-10, 11-20, etc.)
                tab_labels = []
                for i, chunk in enumerate(log_chunks):
                    start_idx = i * chunk_size + 1
                    end_idx = start_idx + len(chunk) - 1
                    tab_labels.append(f"Logs {start_idx}-{end_idx}")
                
                log_tabs = st.tabs(tab_labels)
                
                for t_idx, tab in enumerate(log_tabs):
                    with tab:
                        for log_item in log_chunks[t_idx]:
                            st.markdown(
                                f"""
                                <div style="border: 1px solid #262730; border-radius: 6px; padding: 10px; background-color: #0e1117; margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <b>{log_item['thread_id']}</b> ({log_item['step_cycle']})<br>
                                        <span style="font-size: 11px; color: #888;">{log_item['timestamp']}</span>
                                    </div>
                                    <div style="color: #00ffcc; font-weight: bold; font-size: 13px;">
                                        {log_item['view_status']}
                                    </div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
