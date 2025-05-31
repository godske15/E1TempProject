import streamlit as st
import pandas as pd
import time
import os
import matplotlib.pyplot as plt

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
    padding: 10px;
    font-size: 16px;
}
.filter-container {
    background-color: #f0f2f6;
    padding: 15px;
    border-radius: 15px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="filter-container">', unsafe_allow_html=True)
st.subheader("🔍 Filter Settings")
topic_filter = st.text_input("Filter by topic (leave empty for all topics)", placeholder="Enter topic name...")
st.markdown('</div>', unsafe_allow_html=True)

# Main update loop
df = update_graph()

if not df.empty:
    # Apply topic filter if specified
    if topic_filter:
        filtered_df = df[df['topic'].str.contains(topic_filter, case=False)]
    else:
        filtered_df = df
    
    # Display numerical messages in a chart - MAIN GRAPH (full width)
    try:
        numeric_df = filtered_df.dropna(subset=['numeric_message'])
        
        if not numeric_df.empty:
            st.subheader("📈 Message Values Over Time")
            
            # Use Matplotlib for better control over line rendering
            fig, ax = plt.subplots(figsize=(16, 8))  # Full width figure
            
            # Get unique topics
            topics = numeric_df['topic'].unique()
            
            # Plot each topic as a separate line
            for topic in topics:
                topic_data = numeric_df[numeric_df['topic'] == topic]
                # Sort by timestamp to ensure proper line connections
                topic_data = topic_data.sort_values('timestamp')
                ax.plot(topic_data['timestamp'], topic_data['numeric_message'], 
                       marker='o', label=topic, linewidth=2, markersize=4)
            
            ax.set_xlabel('Time', fontsize=12)
            ax.set_ylabel('Value', fontsize=12)
            ax.legend(fontsize=10)
            ax.grid(True, alpha=0.3)
            
            # Improve layout
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Display the plot
            st.pyplot(fig)
            
        else:
            st.info("No numeric messages found for charting.")
    except Exception as e:
        st.error(f"Could not display chart: {e}")
        st.info("Messages may not be numerical")
    
    # Create layout for bottom section - Recent Messages and Statistics side by side
    col_bottom1, col_bottom2 = st.columns([3, 1])
    
    with col_bottom1:
        # Display the most recent messages
        st.subheader("📋 Recent Messages")
        st.dataframe(filtered_df[['topic', 'message', 'timestamp']].head(5), 
                    use_container_width=True)
    
    with col_bottom2:
        st.subheader("📊 Statistics")
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
            # Execute DELETE query to remove all records from the temp table
            conn.query("DELETE FROM temp", ttl=0)
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
