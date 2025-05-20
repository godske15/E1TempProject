import streamlit as st
import pandas as pd
import time
import os
import matplotlib.pyplot as plt

# Get database path from environment variable or use default
DB_PATH = os.environ.get('DB_PATH', '/sqlite/data/temperatur.db')

# Set up database connection - Fix string formatting
conn = st.connection('sqlite_db', type='sql', url=f'sqlite:///{DB_PATH}')

st.title('MQTT Dashboard')
st.subheader('Messages from MQTT Broker')

# Function to update graph data
def update_graph():
    try:
        # Query data from the temp table
        query = 'SELECT id, topic, message, timestamp FROM temp ORDER BY timestamp DESC LIMIT 100'
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

# Create a layout
col1, col2 = st.columns([3, 1])

with col2:
    # Container for settings and stats
    settings_container = st.container()
    with settings_container:
        st.subheader("Settings")
        # Settings for refresh rate (not necessary)
	refresh_rate = st.slider("Refresh rate (seconds)", 5, 60, 10)
        topic_filter = st.text_input("Filter by topic (leave empty for all)")

# Main update loop
df = update_graph()

if not df.empty:
    # Apply topic filter if specified
    if topic_filter:
        filtered_df = df[df['topic'].str.contains(topic_filter, case=False)]
    else:
        filtered_df = df
    
    with col1:
        # Display numerical messages in a chart - IMPROVED CHART RENDERING
        try:
            numeric_df = filtered_df.dropna(subset=['numeric_message'])
            
            if not numeric_df.empty:
                st.subheader("Message Values Over Time")
                
                # OPTION 1: Use Matplotlib for better control over line rendering
                fig, ax = plt.subplots(figsize=(10, 5))
                
                # Get unique topics
                topics = numeric_df['topic'].unique()
                
                # Plot each topic as a separate line
                for topic in topics:
                    topic_data = numeric_df[numeric_df['topic'] == topic]
                    # Sort by timestamp to ensure proper line connections
                    topic_data = topic_data.sort_values('timestamp')
                    ax.plot(topic_data['timestamp'], topic_data['numeric_message'], 
                           marker='o', label=topic)
                
                ax.set_xlabel('Time')
                ax.set_ylabel('Value')
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # Display the plot
                st.pyplot(fig)
                
                # OPTION 2: Alternative with native Streamlit (as backup)
                # Prepare the data in a format more suitable for Streamlit's line_chart
                # pivot_df = numeric_df.pivot_table(
                #     index='timestamp', 
                #     columns='topic', 
                #     values='numeric_message', 
                #     aggfunc='mean'
                # ).reset_index()
                # pivot_df = pivot_df.set_index('timestamp')
                # st.line_chart(pivot_df)
            else:
                st.info("No numeric messages found for charting.")
        except Exception as e:
            st.error(f"Could not display chart: {e}")
            st.info("Messages may not be numerical")
            
        # Display the most recent messages
        st.subheader("Recent Messages")
        st.dataframe(filtered_df[['topic', 'message', 'timestamp']].head(10), 
                    use_container_width=True)
    
    with col2:
        st.subheader("Statistics")
        st.metric("Total Messages", len(df))
        st.metric("Unique Topics", df['topic'].nunique())
        
        # Show topic distribution
       # st.subheader("Topic Distribution")
       # topic_counts = df['topic'].value_counts().head(5)
       # st.bar_chart(topic_counts)

# Add refresh button
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Implement better auto-refresh using session state
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = time.time()

# Check if it's time to refresh
if time.time() > st.session_state.last_refresh + refresh_rate:
    st.session_state.last_refresh = time.time()
    st.cache_data.clear()
    st.rerun()
