#!/bin/bash

MQTT_BROKER="localhost"
MQTT_TOPIC="#"
DB_PATH="/data/temperatur.db"

echo "Starting MQTT to SQLite logger..."

# Vent et øjeblik for at sikre at MQTT broker er oppe
sleep 10

while true
do
        mosquitto_sub -h "$MQTT_BROKER" -t "$MQTT_TOPIC" | while read -r payload
        do
                echo "Received payload: $payload"
                # Du kan tilpasse parsing her, hvis du sender f.eks. "sensor1:23.5"
                sensor="mqtt_sensor"
                temperatur="$payload"

                # Indsæt i databasen
                sqlite3 "$DB_PATH" "INSERT INTO temperatur_log (måler_navn, temperatur) VALUES ('$sensor', $temperatur);"
        done
        sleep 5
done &

