FROM debian:bookworm-slim

# Installér nødvendige pakker
RUN apt-get update && \
    apt-get install -y sqlite3 mosquitto-clients && \
    rm -rf /var/lib/apt/lists/*

# Sæt arbejdsmappe
WORKDIR /data

# Initier databasen
COPY init.sql /init.sql
RUN sqlite3 temperatur.db < /init.sql

# Kopiér script og giv eksekveringsret
COPY mqtt_logger.sh /data/mqtt_logger.sh
RUN chmod +x /data/mqtt_logger.sh

# Start loggeren
CMD ["/data/mqtt_logger.sh"]

