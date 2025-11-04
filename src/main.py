# src/main.py

import csv
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path

# --- Third-party libraries ---
import paho.mqtt.client as mqtt
import schedule
from gpiozero import MotionSensor, OutputDevice

# Hardware-specific libraries
try:
    from picamera2 import Picamera2
except ImportError:
    print("Warning: picamera2 library not found. Camera functionality will be disabled.")
    Picamera2 = None # Allows script to run without a camera for testing

import adafruit_dht
import board

# --- 1. System Configuration & Setup ---

# Load configuration from file
try:
    with open("config/config.json") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("FATAL: config.json not found. Please ensure it exists in the 'config' directory.")
    exit()
except json.JSONDecodeError:
    print("FATAL: Could not parse config.json. Check for syntax errors.")
    exit()

# Create necessary directories from config
Path(config["logging"]["data_path"]).mkdir(exist_ok=True)
Path(config["logging"]["image_path"]).mkdir(exist_ok=True)
Path("logs").mkdir(exist_ok=True)

# Setup logging to file
logging.basicConfig(
    filename=config["logging"]["log_file"],
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
print(f"Application starting... Logging to '{config['logging']['log_file']}'")
logging.info("Application starting...")

# --- 2. Global State & Hardware Initialization ---

# System state variables
current_system_mode = "Home"  # Default mode: "Home", "Away", "Night"
last_motion_time = 0

# Initialize Hardware (with error handling)
try:
    pir = MotionSensor(config["pins"]["pir_sensor"])
    logging.info(f"PIR sensor initialized on GPIO {config['pins']['pir_sensor']}.")
except Exception as e:
    logging.error(f"Failed to initialize PIR sensor: {e}")
    pir = None

try:
    # Use getattr to dynamically get the board pin object
    dht_sensor_pin = getattr(board, f'D{config["pins"]["dht_sensor"]}')
    dht_device = adafruit_dht.DHT11(dht_sensor_pin) # CORRECTED: Changed to DHT11 for your sensor
    logging.info(f"DHT11 sensor initialized on GPIO {config['pins']['dht_sensor']}.") # CORRECTED: Log message
except Exception as e:
    logging.error(f"Failed to initialize DHT11 sensor: {e}") # CORRECTED: Log message
    dht_device = None

# Actuators (meets the >=3 requirement)
led_light = OutputDevice(config["pins"]["led_light"])
fan_relay = OutputDevice(config["pins"]["fan_relay"])
buzzer = OutputDevice(config["pins"]["buzzer"])

# Camera
picam2 = None
if Picamera2:
    try:
        picam2 = Picamera2()
        camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)})
        picam2.configure(camera_config)
        picam2.start()
        time.sleep(2) # Allow camera to warm up
        logging.info("Camera initialized successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize camera: {e}")
        picam2 = None
else:
    logging.warning("Camera is disabled because picamera2 library is not available.")

# --- 3. MQTT Client for Adafruit IO ---

AIO_CONFIG = config["adafruit_io"]
MQTT_CLIENT = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="rpi-home-security-client")

def on_connect(client, userdata, flags, rc, properties):
    if rc == 0:
        logging.info("Connected to Adafruit IO MQTT Broker.")
        print("Successfully connected to Adafruit IO!")
        # Subscribe to all control feeds
        for key, feed in AIO_CONFIG["feeds"].items():
            if "control" in key or "mode" in key:
                client.subscribe(feed)
                logging.info(f"Subscribed to feed: {feed}")
    else:
        logging.error(f"Failed to connect to MQTT, return code {rc}")

def on_message(client, userdata, msg):
    global current_system_mode
    payload = msg.payload.decode()
    logging.info(f"Received message on topic {msg.topic}: {payload}")

    if msg.topic == AIO_CONFIG["feeds"]["light_control"]:
        led_light.on() if payload == "1" else led_light.off()
        log_data({"event_type": "actuator_change", "device": "led_light", "state": led_light.value})
    elif msg.topic == AIO_CONFIG["feeds"]["fan_control"]:
        fan_relay.on() if payload == "1" else fan_relay.off()
        log_data({"event_type": "actuator_change", "device": "fan_relay", "state": fan_relay.value})
    elif msg.topic == AIO_CONFIG["feeds"]["system_mode"]:
        current_system_mode = payload
        log_data({"event_type": "mode_change", "new_mode": current_system_mode})
        print(f"System mode changed to: {current_system_mode}")

def setup_mqtt_client():
    MQTT_CLIENT.username_pw_set(AIO_CONFIG["username"], AIO_CONFIG["api_key"])
    MQTT_CLIENT.on_connect = on_connect
    MQTT_CLIENT.on_message = on_message
    try:
        MQTT_CLIENT.connect("io.adafruit.com", 1883, 60)
        MQTT_CLIENT.loop_start()  # Starts a background thread for MQTT
    except Exception as e:
        logging.error(f"Could not connect to MQTT broker: {e}")

# --- 4. Core Application Logic & Event Handlers ---

def handle_motion():
    global last_motion_time
    # Motion is only a security event if the system is in 'Away' mode
    if current_system_mode != "Away":
        logging.info(f"Motion detected, but system mode is '{current_system_mode}'. Ignoring.")
        return

    current_time = time.time()
    if (current_time - last_motion_time) < config["settings"]["motion_debounce"]:
        logging.warning("Motion detected, but within debounce period. Ignoring.")
        return

    last_motion_time = current_time
    logging.info("SECURITY ALERT: Motion detected while in 'Away' mode!")
    print("SECURITY ALERT: Motion detected!")
    
    # Trigger actuators for an alert
    buzzer.on()
    
    # Publish alert to Adafruit IO
    MQTT_CLIENT.publish(AIO_CONFIG["feeds"]["motion_state"], "1")
    
    # Capture image in a separate thread to avoid blocking
    if picam2:
        capture_thread = threading.Thread(target=capture_image_and_alert)
        capture_thread.start()

    # Log the event
    log_data({"event_type": "motion_detected", "details": "System was in Away mode"})
    
    # Schedule the 'all clear' reset
    threading.Timer(10.0, reset_motion_state).start()

def reset_motion_state():
    logging.info("Resetting motion state.")
    buzzer.off()
    MQTT_CLIENT.publish(AIO_CONFIG["feeds"]["motion_state"], "0")

def capture_image_and_alert():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = Path(config["logging"]["image_path"]) / f"motion_{timestamp}.jpg"
    try:
        picam2.capture_file(str(image_path))
        logging.info(f"Image captured: {image_path}")
        # Publish the timestamp of the new image
        MQTT_CLIENT.publish(AIO_CONFIG["feeds"]["camera_timestamp"], datetime.now().isoformat())
    except Exception as e:
        logging.error(f"Failed to capture image: {e}")

def read_and_publish_sensors():
    if not dht_device:
        return
    try:
        temp = dht_device.temperature
        humidity = dht_device.humidity
        if temp is not None and humidity is not None:
            logging.info(f"Read Temp={temp:.1f}*C, Humidity={humidity:.1f}%")
            # Publish to Adafruit IO
            MQTT_CLIENT.publish(AIO_CONFIG["feeds"]["temperature"], f"{temp:.2f}")
            MQTT_CLIENT.publish(AIO_CONFIG["feeds"]["humidity"], f"{humidity:.2f}") # CORRECTED: Fixed typo from 'hum'
            # Log to local file
            log_data({"event_type": "sensor_reading", "temperature_c": temp, "humidity_percent": humidity})
    except RuntimeError as e:
        logging.warning(f"DHT sensor read error: {e}")
    except Exception as e:
        logging.error(f"Unexpected DHT sensor error: {e}")


# --- 5. Data Logging (CSV) ---

def get_log_filename():
    date_stamp = datetime.now().strftime("%Y-%m-%d")
    return Path(config["logging"]["data_path"]) / f"{date_stamp}_home_env.csv"

def log_data(data_dict):
    log_file = get_log_filename()
    # Prepend timestamp and actuator states to every log entry
    full_log_entry = {
        "timestamp": datetime.now().isoformat(),
        "led_state": led_light.value,
        "fan_state": fan_relay.value,
        **data_dict
    }

    header = list(full_log_entry.keys())
    values = [str(full_log_entry.get(h, '')) for h in header] # Get value or empty string

    try:
        is_new_file = not log_file.exists()
        with open(log_file, "a", newline='') as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow(header) # Write header only if file is new
            writer.writerow(values)
    except IOError as e:
        logging.error(f"Could not write to log file {log_file}: {e}")


# --- 6. Daily Cloud Upload ---

def upload_previous_days_log():
    """
    This function finds yesterday's log file and uploads it to a cloud service.
    This is a placeholder that requires you to complete the authentication.
    """
    yesterday = datetime.now() - timedelta(days=1)
    date_stamp = yesterday.strftime("%Y-%m-%d")
    log_file_to_upload = Path(config["logging"]["data_path"]) / f"{date_stamp}_home_env.csv"

    if log_file_to_upload.exists():
        logging.info(f"Attempting to upload {log_file_to_upload} to the cloud...")
        print(f"--> Found log file from yesterday: {log_file_to_upload}. Starting upload process.")
        
        # --- UPLOAD LOGIC: To be completed by you ---
        # This example uses PyDrive2 for Google Drive.
        # You must follow the PyDrive2 setup instructions to create 'client_secrets.json'
        # The first time you run this, it will open a browser for you to log in and authorize.
        try:
            from pydrive2.auth import GoogleAuth
            from pydrive2.drive import GoogleDrive

            gauth = GoogleAuth()
            # This will use a local web server to authenticate you.
            gauth.LocalWebserverAuth()
            drive = GoogleDrive(gauth)

            # Find a folder ID on your Google Drive where you want to upload files.
            # You can get this from the URL of the folder.
            folder_id = "YOUR_GOOGLE_DRIVE_FOLDER_ID_HERE"
            
            file_drive = drive.CreateFile({
                'title': log_file_to_upload.name,
                'parents': [{'id': folder_id}]
            })
            file_drive.SetContentFile(str(log_file_to_upload))
            file_drive.Upload()
            logging.info("Upload successful.")
            print(f"--> Successfully uploaded {log_file_to_upload.name} to Google Drive.")

        except Exception as e:
            logging.error(f"Cloud upload failed: {e}")
            print(f"--> ERROR: Cloud upload failed. Check logs/app.log. The file remains locally.")
    else:
        logging.warning(f"Log file for {date_stamp} not found. Nothing to upload.")
        print(f"--> No log file found for yesterday ({date_stamp}). Nothing to upload.")

# --- 7. Main Loop and Scheduler ---

def main():
    logging.info("Starting main application services.")
    
    # Setup MQTT
    setup_mqtt_client()
    
    # Bind the motion handler to the PIR sensor if it exists
    if pir:
        pir.when_motion = handle_motion
    
    # Schedule periodic tasks
    schedule.every(30).seconds.do(read_and_publish_sensors)
    schedule.every().day.at("00:05").do(upload_previous_days_log) # As per requirements
    
    print("Application is running. Press CTRL+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nApplication stopped by user.")
    finally:
        if dht_device:
            dht_device.exit()
        MQTT_CLIENT.loop_stop()
        MQTT_CLIENT.disconnect()
        logging.info("Cleaned up resources and shutting down.")
        print("Cleanup complete. Exiting.")

if __name__ == "__main__":
    main()
