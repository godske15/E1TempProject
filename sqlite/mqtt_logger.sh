#!/bin/sh

# Create SQLite database if it doesn't exist
sqlite3 /data/temperatur.db "CREATE TABLE IF NOT EXISTS temp (id INTEGER PRIMARY KEY AUTOINCREMENT, topic TEXT, message TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);"

# Subscribe to all topics and pipe to while loop to process each message
# -v  outputs both topic and message on the same line
# Then we divide the output into topic and message with "while read -r topic message
mosquitto_sub -h $MQTT_BROKER_HOST -p $MQTT_BROKER_PORT -t '#' -v | while read -r topic message
do

  # Store message in SQLite database
  sqlite3 /data/temperatur.db "INSERT INTO temp (topic, message) VALUES ('$topic', '$message');"

  # Write out to the terminal the topic and message recieved
  echo "Stored message from topic $topic: $message"
done
