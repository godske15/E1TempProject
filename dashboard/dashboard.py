import streamlit as st
import pandas as pd
import time
import os
import matplotlib.pyplot as plt
from sqlalchemy import text

# Get database path from environment variable or use default
DB_PATH = os.environ.get('DB_PATH', '/sqlite/data/temperatur.db')

# Set up database connection
conn = st.connection('sqlite_db', type='sql', url=f'sqlite:///{DB_PATH}')

# Function to update graph data
def update_graph():
    try:
        # Query data from the temp table - increased limit to 10000
        query = 'SELECT id, topic, message, timestamp FROM temp ORDER BY timestamp DESC LIMIT 10000'
        data = conn.query(query)
        if not data.empty:
            # Convert to dataframe for visualization
            df = pd.DataFrame(data)
            # Convert timestamp to datetime if needed
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            # Convert message to numeric values where possible
            df['numeric_message'] = pd.to_numeric(df['message'], errors='coerce')
            return df
        else:
            st.warning("No data found in the database.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error querying database: {e}")
        return pd.DataFrame()

# Topic filter with improved styling
st.markdown("""
<style>
.stTextInput > div > div > input {
    border-radius: 15px;
    border: 2px solid #4CAF50;
    padding: 8px;
    font-size: 14px;
}
.filter-container {
    background-color: #f0f2f6;
    padding: 10px;
    border-radius: 10px;
    margin-bottom: 15px;
}
.alarm-box {
    background-color: #ffebee;
    border: 3px solid #f44336;
    border-radius: 10px;
    padding: 14px;
    margin: 10px 0;
    animation: blink 1s linear infinite;
}
@keyframes blink {
    50% { opacity: 0.5; }
}
.warning-box {
    background-color: #fff3e0;
    border: 2px solid #ff9800;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}
.success-box {
    background-color: #e8f5e8;
    border: 2px solid #4caf50;
    border-radius: 8px;
    padding: 12px;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

# Initialize topic_filter from session state or empty string
if 'topic_filter' not in st.session_state:
    st.session_state.topic_filter = ""

# Main update loop
df = update_graph()

if not df.empty:
    # Apply topic filter if specified
    if st.session_state.topic_filter:
        filtered_df = df[df['topic'].str.contains(st.session_state.topic_filter, case=False)]
    else:
        filtered_df = df
    
    # Temperature alarm system - check latest values for each topic (moved before graph)
    numeric_df = filtered_df.dropna(subset=['numeric_message'])
    if not numeric_df.empty:
        # Get the latest temperature reading for each topic
        latest_temps = numeric_df.groupby('topic')['numeric_message'].last().reset_index()
        latest_temps = latest_temps.sort_values('numeric_message')
        
        # Check alarm conditions
        alarm_triggered = False
        alarm_message = ""
        
        if len(latest_temps) >= 2:
            lowest_temp = latest_temps.iloc[0]['numeric_message']
            lowest_topic = latest_temps.iloc[0]['topic']
            highest_temp = latest_temps.iloc[-1]['numeric_message']
            highest_topic = latest_temps.iloc[-1]['topic']
            
            # Check if lowest temperature is over 55°C
            if lowest_temp > 55:
                alarm_triggered = True
                alarm_message = f"TEMPERATURE ALARM: Lowest temperature ({lowest_topic}: {lowest_temp:.1f}°C) exceeds 55°C limit!"
            
            # Additional check: ensure one topic is in 59-60°C range
            temp_in_range = any(59 <= temp <= 60 for temp in latest_temps['numeric_message'])
            if not temp_in_range and highest_temp < 59:
                st.markdown(f'<div class="warning-box"><strong>Warning:</strong> No temperature in optimal 59-60°C range. Highest: {highest_topic}: {highest_temp:.1f}°C</div>', unsafe_allow_html=True)
        
        # Display alarm if triggered
        if alarm_triggered:
            st.markdown(f'<div class="alarm-box"><h4 style="color: #d32f2f; margin: 0;">CRITICAL TEMPERATURE ALERT</h4><p style="margin: 5px 0; font-size: 14px;"><strong>Current temperatures:</strong></p>', unsafe_allow_html=True)
            
            for _, row in latest_temps.iterrows():
                color = "#d32f2f" if row['numeric_message'] > 55 else "#2e7d32"
                st.markdown(f"<p style='margin: 2px 0; color: {color}; font-size: 12px;'><strong>{row['topic']}: {row['numeric_message']:.1f}°C</strong></p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Show current status when no alarm
            if len(latest_temps) >= 1:
                st.markdown('<div class="success-box"><strong>Status:</strong> Temperature levels OK</div>', unsafe_allow_html=True)
                temp_readings = " | ".join([f"{row['topic']}: {row['numeric_message']:.1f}°C" for _, row in latest_temps.iterrows()])
                st.markdown(f'<div style="font-size: 12px; padding: 5px; background-color: #f5f5f5; border-radius: 5px; margin: 5px 0;">Current: {temp_readings}</div>', unsafe_allow_html=True)

    # Display numerical messages in a chart - MAIN GRAPH (now full width)
    # Display numerical messages in a chart - MAIN GRAPH (now full width)
    try:
        numeric_df = filtered_df.dropna(subset=['numeric_message'])
        
        if not numeric_df.empty:
            st.subheader("Message Values Over Time")
            
            # Use Matplotlib for better control over line rendering
            fig, ax = plt.subplots(figsize=(26, 12))  # Much larger graph size
            
            # Get unique topics
            topics = numeric_df['topic'].unique()
            
            # Plot each topic as a separate line
            for topic in topics:
                topic_data = numeric_df[numeric_df['topic'] == topic]
                # Sort by timestamp to ensure proper line connections
                topic_data = topic_data.sort_values('timestamp')
                ax.plot(topic_data['timestamp'], topic_data['numeric_message'], 
                       marker='o', label=topic, linewidth=2, markersize=4)
            
            # Add horizontal lines for temperature thresholds
            ax.axhline(y=55, color='red', linestyle='--', alpha=0.7, label='55°C Limit')
            ax.axhline(y=59, color='orange', linestyle='--', alpha=0.7, label='59°C Target Min')
            ax.axhline(y=60, color='green', linestyle='--', alpha=0.7, label='60°C Target Max')
            
            ax.set_xlabel('Time', fontsize=16)
            ax.set_ylabel('Temperature (°C)', fontsize=16)
            ax.legend(fontsize=14)
            ax.grid(True, alpha=0.3)
            
            # Improve layout with larger tick font
            plt.xticks(rotation=45, fontsize=14)
            plt.yticks(fontsize=14)
            plt.tight_layout()
            
            # Display the plot
            st.pyplot(fig)
            
        else:
            st.info("No numeric messages found for charting.")
    except Exception as e:
        st.error(f"Could not display chart: {e}")
        st.info("Messages may not be numerical")
    
    # Filter by topic input - positioned between graph and recent messages
    col_filter, col_spacer = st.columns([2, 2])
    with col_filter:
        st.session_state.topic_filter = st.text_input("Filter by topic", 
                                                      value=st.session_state.topic_filter,
                                                      placeholder="Enter topic name...")
    
    # Create layout for bottom section - Recent Messages and Statistics side by side
    col_bottom1, col_bottom2 = st.columns([3, 1])
    
    with col_bottom1:
        # Display the most recent messages
        st.subheader("Recent Messages")
        st.dataframe(filtered_df[['topic', 'message', 'timestamp']].head(5), 
                    use_container_width=True)
    
    with col_bottom2:
        st.subheader("Statistics")
        st.metric("Total Messages", len(df))

# Add refresh and reset buttons
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()

with col_btn2:
    if st.button("Reset Database", type="secondary"):
        try:
            # Execute DELETE query using the underlying connection with text wrapper
            with conn._instance.connect() as connection:
                connection.execute(text("DELETE FROM temp"))
                connection.commit()
            st.success("Database reset successfully! All data has been cleared.")
            st.cache_data.clear()
            time.sleep(1)  # Brief pause to show the success message
            st.rerun()
        except Exception as e:
            st.error(f"Error resetting database: {e}")

# Implement auto-refresh with fixed 10 second interval
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Check if it's time to refresh (fixed 10 second refresh rate)
if time.time() > st.session_state.last_refresh + 10:
    st.session_state.last_refresh = time.time()
    st.cache_data.clear()
    st.rerun()
