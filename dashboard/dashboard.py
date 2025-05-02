import streamlit as st
import pandas as pd
import time

conn = st.connection('test_db', type='sql', url='sqlite:///test.db')

def updateGraph():
    conn = st.connection('test_db', type='sql', url='sqlite:///test.db')
    sensors = conn.query('SELECT * FROM sensorreadings')  # sørg for at tabellenavn er korrekt
    sensors_df = pd.DataFrame(sensors)
    return sensors_df

# Main Streamlit app
placeholder = st.empty()

while True:
    df = updateGraph()
    with placeholder.container():
        st.line_chart(df)
    time.sleep(10)
    st.cache_data.clear()
    st.rerun()
