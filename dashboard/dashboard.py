import streamlit as st
import pandas as pd
import time
import os

# Get database path from environment variable or use default
DB_PATH = os.environ.get('DB_PATH', '/sqlite/data/temperatur.db')

# Set up database connection
conn = st.connection('sqlite_db', type='sql', url='sqlite:///{DB_PATH}')

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
            return df
        else:
            st.warning("No data found in the database.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error querying database: {e}")
        return pd.DataFrame()

# Create a layout
col1, col2 = st.columns([3, 1])

with col1:
    # Container for the charts and tables
    main_container = st.container()
    
with col2:
    # Container for settings and stats
    settings_container = st.container()
    with settings_container:
        st.subheader("Settings")
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
    
    with main_container:
        # Display numerical messages in a chart if possible
        try:
            # Try to convert message to numeric values
            numeric_df = filtered_df.copy()
            numeric_df['numeric_message'] = pd.to_numeric(numeric_df['message'], errors='coerce')
            numeric_df = numeric_df.dropna(subset=['numeric_message'])

            if not numeric_df.empty:
                st.subheader("Message Values Over Time")
                chart_df = numeric_df.groupby(['topic', 'timestamp'])['numeric_message'].mean().unstack('topic')
                st.line_chart(chart_df)
            else:
                st.info("No numeric messages found for charting.")
        except Exception as e:
            st.info("Could not display chart: messages are not numerical")

        # Display the most recent messages
        st.subheader("Recent Messages")
        st.dataframe(filtered_df[['topic', 'message', 'timestamp']].head(10), 
                     use_container_width=True)
    
    with settings_container:
        st.subheader("Statistics")
        st.metric("Total Messages", len(df))
        st.metric("Unique Topics", df['topic'].nunique())

        # Show topic distribution
        st.subheader("Topic Distribution")
        topic_counts = df['topic'].value_counts().head(5)
        st.bar_chart(topic_counts)

# Auto refresh button and functionality
if st.button("Refresh Data"):
    st.cache_data.clear()
    st.rerun()

# Add auto-refresh
time.sleep(refresh_rate)
st.cache_data.clear()
st.rerun()
