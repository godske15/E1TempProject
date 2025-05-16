# Use the official Eclipse Mosquitto image as the base
FROM eclipse-mosquitto:latest

# Set the maintainer label
LABEL maintainer="your-name <you@example.com>"

# Expose MQTT port
# EXPOSE 1883

# Expose MQTT over WebSockets port (if needed)
# EXPOSE 9001

# Copy custom configuration file (if you have one)
COPY config/mosquitto.conf /mosquitto/config/mosquitto.conf
COPY log/mosquitto.log /mosquitto/log/mosquitto.log
# COPY config/password /mosquitto/config/password

# Set the entrypoint to run Mosquitto
ENTRYPOINT ["/usr/sbin/mosquitto", "-c", "/mosquitto/config/mosquitto.conf"]
