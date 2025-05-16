FROM debian:bookworm-slim

# Installér nødvendige pakker
RUN apt-get update && \
    apt-get install -y sqlite3 mosquitto-clients && \
    rm -rf /var/lib/apt/lists/*

# Sæt arbejdsmappe
# WORKDIR /data
# RUN chmod 777 /data

# Initier databasen
COPY init.sql /init.sql
RUN sqlite3 /data/temperatur.db

# Kopiér script og giv eksekveringsret
COPY mqtt_logger.sh /mqtt_logger.sh
RUN chmod +x /mqtt_logger.sh

# Start loggeren
CMD ["/mqtt_logger.sh"]

