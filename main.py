# src/main.py

import json
import time
import paho.mqtt.client as mqtt
from pathlib import Path

# --- 1. Load Configuration ---
# This looks for the config file relative to the project root.
try:
    config_path = Path("config/config.json")
    with config_path.open() as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print(f"Error: Configuration file not found at {config_path}")
    exit()
except json.JSONDecodeError:
    print(f"Error: Could not parse {config_path}. Make sure it is valid JSON.")
    exit()

# --- 2. Adafruit IO & MQTT Setup ---
AIO_CONFIG = config["adafruit_io"]
AIO_USERNAME = AIO_CONFIG["username"]
AIO_KEY = AIO_CONFIG["api_key"]
AIO_HOST = "io.adafruit.com"
AIO_PORT = 1883

# Define the feeds we will use from the config file
feed_temperature = AIO_CONFIG["feeds"]["temperature"]
feed_light_control = AIO_CONFIG["feeds"]["light_control"]

# --- 3. MQTT Callback Functions ---

# This function is called when the client successfully connects to the broker.
def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        print("Successfully connected to Adafruit IO!")
        # Once connected, we subscribe to the feeds we want to listen to.
        print(f"Subscribing to feed: {feed_light_control}")
        client.subscribe(feed_light_control)
    else:
        print(f"Failed to connect, return code {rc}\n")

# This function is called when a message is received from a subscribed feed.
def on_message(client, userdata, msg):
    print(f"Received message from `{msg.topic}`: {msg.payload.decode()}")
    
    # Example: Control a real or virtual LED based on the message
    if msg.topic == feed_light_control:
        if msg.payload.decode() == "1":
            print("--> Light control turned ON")
            # Add your gpiozero code here: led.on()
        else:
            print("--> Light control turned OFF")
            # Add your gpiozero code here: led.off()

# --- 4. Main Application Logic ---

def main():
    # Create an MQTT client
    # Using VERSION2 is recommended for the new `properties` argument in on_connect
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="rpi-client-1")

    # Set the username and password for authentication
    client.username_pw_set(username=AIO_USERNAME, password=AIO_KEY)

    # Assign the callback functions
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the broker
    try:
        client.connect(AIO_HOST, AIO_PORT, 60)
    except Exception as e:
        print(f"Could not connect to MQTT broker: {e}")
        return

    # Start a non-blocking background loop to handle network traffic and callbacks.
    client.loop_start()

    print("Starting main loop to publish data every 10 seconds...")
    simulated_temp = 20.0
    try:
        while True:
            # In a real application, you would read this from your DHT sensor.
            # For this example, we'll just simulate changing data.
            simulated_temp += 0.5
            if simulated_temp > 30:
                simulated_temp = 20.0

            print(f"Publishing simulated temperature value: {simulated_temp:.2f} to feed `{feed_temperature}`")
            
            # Publish the data to your Adafruit IO feed
            client.publish(feed_temperature, f"{simulated_temp:.2f}")
            
            # Wait for 10 seconds before sending the next value
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nScript stopped by user.")
    finally:
        # Stop the network loop and disconnect cleanly
        print("Disconnecting from Adafruit IO...")
        client.loop_stop()
        client.disconnect()

# This ensures the main() function is called when the script is executed
if __name__ == "__main__":
    main()
