FROM python:3.9-slim

# Install required Python packages
RUN pip install --no-cache-dir streamlit pandas sqlalchemy matplotlib

# Copy the Streamlit app
COPY dashboard.py /dashboard.py

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "--server.port=8501", "--server.address=0.0.0.0", "dashboard.py"]
