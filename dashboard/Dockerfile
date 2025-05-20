FROM python:3.9-slim

WORKDIR /app

# Install required Python packages and dependencies for matplotlib
RUN apt-get update && apt-get install -y \
    build-essential \
    libfreetype6-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip install --no-cache-dir streamlit pandas sqlalchemy matplotlib

# Copy just the application code
COPY dashboard.py ./dashboard.py

# Set environment variables to disable file watching
ENV STREAMLIT_SERVER_ENABLECORS=false \
    STREAMLIT_SERVER_ENABLEXSRFPROTECTION=false \
    STREAMLIT_SERVER_ENABLEWEBSOCKETCOMPRESSION=false \
    WATCHDOG_NO_INOTIFY=1 \
    STREAMLIT_SERVER_FILEWATCH_DISABLED=true

# Expose the Streamlit port
EXPOSE 8501

# Run the Streamlit app
CMD ["streamlit", "run", "--server.port=8501", "--server.address=0.0.0.0", "dashboard.py"]
