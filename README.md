# IoT Home Security System

A Raspberry Pi-based home security and automation system with motion detection, environmental monitoring, and remote control capabilities via Adafruit IO.

## Video Link
https://www.youtube.com/shorts/agyrXt_8QSU

## Team Members

- Jeremy Roos 2332918
- Jeremy Misola 2330210
- Andy Le 2330800

## System Overview

This IoT home security system monitors and protects your home using multiple sensors and actuators controlled by a Raspberry Pi. The system operates in three modes:

- **Home Mode**: Normal operation with environmental monitoring only
- **Away Mode**: Full security mode with motion detection and camera alerts
- **Night Mode**: Reduced sensitivity monitoring

### Key Features

- Motion detection with PIR sensor triggers security alerts
- Automatic photo capture when motion is detected in Away mode
- Temperature and humidity monitoring (DHT11 sensor)
- Remote control of LED lights and fan via Adafruit IO dashboard
- Buzzer alarm for security alerts
- Data logging to CSV files with daily cloud backup
- MQTT communication for real-time updates

### Block Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Raspberry Pi 4                          │
│                                                             │
│  ┌──────────────┐        ┌──────────────┐                 │
│  │   main.py    │◄──────►│  Adafruit IO │                 │
│  │  (Python)    │  MQTT  │     Cloud    │                 │
│  └──────┬───────┘        └──────────────┘                 │
│         │                                                   │
│    ┌────┴────┐                                             │
│    │  GPIO   │                                             │
│    └────┬────┘                                             │
└─────────┼──────────────────────────────────────────────────┘
          │
    ──────┴──────────────────────────────────────────────
    │          │         │         │         │         │
┌───▼───┐  ┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌───▼────┐ ┌──▼───┐
│  PIR  │  │ DHT11 │ │ LED  │ │ Fan  │ │Camera  │ │Buzzer│
│Sensor │  │Sensor │ │Light │ │Relay │ │ Pi Cam │ │      │
└───────┘  └───────┘ └──────┘ └──────┘ └────────┘ └──────┘
```

## Bill of Materials

| Component | Model | Quantity | Link |
|-----------|-------|----------|------|
| Microcontroller | Raspberry Pi 4 Model B (4GB RAM) | 1 | [Adafruit](https://www.adafruit.com/product/4296) |
| Motion Sensor | HC-SR501 PIR Motion Sensor | 1 | [Amazon](https://www.amazon.com/s?k=HC-SR501) |
| Temperature/Humidity | DHT11 Digital Sensor | 1 | [Adafruit](https://www.adafruit.com/product/386) |
| Camera | Raspberry Pi Camera Module v2 | 1 | [Adafruit](https://www.adafruit.com/product/3099) |
| LED | 5mm LED with 220Ω resistor | 1 | [Generic] |
| Fan Control | 5V Relay Module | 1 | [Amazon](https://www.amazon.com/s?k=5v+relay+module) |
| Buzzer | Active Buzzer 5V | 1 | [Amazon](https://www.amazon.com/s?k=5v+active+buzzer) |
| Power Supply | 5V 3A USB-C Power Supply | 1 | [Official RPi Store] |
| SD Card | 32GB microSD Card (Class 10) | 1 | [Generic] |
| Breadboard | 830-point Solderless Breadboard | 1 | [Generic] |
| Jumper Wires | Male-to-Female/Male-to-Male | 1 pack | [Generic] |

**Estimated Total Cost**: ~$120-150 USD

## Wiring Diagram

### GPIO Pin Assignments

| Component | GPIO Pin | Physical Pin |
|-----------|----------|--------------|
| PIR Sensor | GPIO 17 | Pin 11 |
| DHT11 Sensor | GPIO 22 | Pin 15 |
| LED Light | GPIO 23 | Pin 16 |
| Fan Relay | GPIO 24 | Pin 18 |
| Buzzer | GPIO 25 | Pin 22 |
| Camera | CSI Port | Camera Port |

### Schematic

```
Raspberry Pi 5
┌─────────────────────┐
│                     │
│  GPIO 17 ─────────► PIR Sensor (Signal)
│  GPIO 22 ─────────► DHT11 (Data)
│  GPIO 23 ─────────► LED (+) via 220Ω resistor
│  GPIO 24 ─────────► Relay (IN)
│  GPIO 25 ─────────► Buzzer (+)
│                     │
│  3.3V ─────────────► DHT11 (VCC), PIR (VCC)
│  5V ───────────────► Relay (VCC), Buzzer (VCC via relay if needed)
│  GND ──────────────► All components (Ground)
│                     │
└─────────────────────┘

Notes:
- LED requires 220Ω current-limiting resistor
- DHT11 may require 10kΩ pull-up resistor on data line
- Relay controls external fan power circuit
- PIR sensor has 3 pins: VCC, GND, OUT
```

### Photos

#### Hardware Setup

<img width="463" height="550" alt="image" src="https://github.com/user-attachments/assets/4ccd095b-e72f-4a36-ad17-35e612fc5d24" />
*Complete system housed in custom enclosure with Raspberry Pi, breadboard, and all sensors*

<img width="231" height="281" alt="image" src="https://github.com/user-attachments/assets/c27e2eab-651b-4537-8b53-d6cbca7f0926" />
*Detailed view of component wiring on breadboard showing PIR sensor (blue), DHT11 sensor, relay module, and LED connections*

#### Adafruit IO Dashboard

<img width="350" height="363" alt="image" src="https://github.com/user-attachments/assets/c139c8af-f5ca-44d7-927d-e4eb14d8c877" />
*Dashboard showing humidity graph and motion indicator (OFF state) with mobile notification toggle*

<img width="232" height="356" alt="image" src="https://github.com/user-attachments/assets/28310cfd-03d3-4034-968f-ca9512f29f9d" />
*Temperature and humidity monitoring graphs with light control toggle (ON state) and system statistics*

## Setup Instructions

### 1. Operating System Preparation

**Install Raspberry Pi OS Lite (64-bit recommended)**

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-venv git
```

### 2. Enable Hardware Interfaces

```bash
# Enable camera and I2C
sudo raspi-config
# Navigate to: Interface Options > Camera > Enable
# Navigate to: Interface Options > I2C > Enable
# Reboot when prompted
sudo reboot
```

### 3. Project Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/iot-home-security.git
cd iot-home-security

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 4. Dependencies

**Create `requirements.txt` file:**

```
paho-mqtt==1.6.1
gpiozero==2.0
picamera2==0.3.12
adafruit-circuitpython-dht==4.0.0
schedule==1.2.0
PyDrive2==1.15.0
```

**Additional system packages:**

```bash
sudo apt install -y libgpiod2 python3-libcamera python3-picamera2
```

### 5. Configuration

**Create `config/config.json`:**

```json
{
  "adafruit_io": {
    "username": "YOUR_AIO_USERNAME",
    "api_key": "YOUR_AIO_KEY",
    "feeds": {
      "temperature": "YOUR_USERNAME/feeds/temperature",
      "humidity": "YOUR_USERNAME/feeds/humidity",
      "motion_state": "YOUR_USERNAME/feeds/motion",
      "light_control": "YOUR_USERNAME/feeds/light",
      "fan_control": "YOUR_USERNAME/feeds/fan",
      "system_mode": "YOUR_USERNAME/feeds/mode",
      "camera_timestamp": "YOUR_USERNAME/feeds/camera"
    }
  },
  "pins": {
    "pir_sensor": 17,
    "dht_sensor": 22,
    "led_light": 23,
    "fan_relay": 24,
    "buzzer": 25
  },
  "settings": {
    "motion_debounce": 30
  },
  "logging": {
    "log_file": "logs/app.log",
    "data_path": "data",
    "image_path": "images"
  }
}
```

### 6. Adafruit IO Setup

1. Create account at [io.adafruit.com](https://io.adafruit.com)
2. Create the following feeds:
   - `temperature`
   - `humidity`
   - `motion`
   - `light`
   - `fan`
   - `mode`
   - `camera`
3. Create a dashboard and add blocks for each feed
4. Copy your AIO Key from account settings
5. Update `config/config.json` with your credentials

### 7. Google Drive Setup (Optional - for cloud backup)

```bash
# Install PyDrive2
pip install PyDrive2

# Follow PyDrive2 setup instructions to create client_secrets.json
# First run will open browser for authentication
```

## How to Run

### Manual Execution

```bash
# Activate virtual environment
source venv/bin/activate

# Run the application
python src/main.py
```

### Run as systemd Service (Recommended)

**Create service file: `/etc/systemd/system/home-security.service`**

```ini
[Unit]
Description=IoT Home Security System
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/iot-home-security
ExecStart=/home/pi/iot-home-security/venv/bin/python /home/pi/iot-home-security/src/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**

```bash
sudo systemctl daemon-reload
sudo systemctl enable home-security.service
sudo systemctl start home-security.service

# Check status
sudo systemctl status home-security.service

# View logs
sudo journalctl -u home-security.service -f
```

## Data Format Specification

### CSV Log Format

**Filename**: `YYYY-MM-DD_home_env.csv`

**Fields**:

| Field | Type | Unit | Description |
|-------|------|------|-------------|
| timestamp | ISO 8601 string | - | Event timestamp |
| led_state | Integer | boolean | LED state (0=off, 1=on) |
| fan_state | Integer | boolean | Fan state (0=off, 1=on) |
| event_type | String | - | Type of event logged |
| temperature_c | Float | °C | Temperature (if sensor reading) |
| humidity_percent | Float | % | Relative humidity (if sensor reading) |
| device | String | - | Actuator name (if actuator change) |
| state | Integer | boolean | New actuator state (if actuator change) |
| new_mode | String | - | System mode (if mode change) |
| details | String | - | Additional event information |

**Example Entries**:

```csv
timestamp,led_state,fan_state,event_type,temperature_c,humidity_percent
2025-11-04T08:15:23.456789,0,0,sensor_reading,22.5,45.0
2025-11-04T08:15:53.123456,1,0,actuator_change,,,led_light,1
2025-11-04T08:16:10.789012,1,0,motion_detected,,,,,"System was in Away mode"
2025-11-04T08:20:05.234567,1,0,mode_change,,,,,Home
```

### File Rotation Policy

- **New file created**: Daily at midnight (00:00:00 local time)
- **Filename pattern**: `YYYY-MM-DD_home_env.csv`
- **Retention**: All files retained locally
- **Cloud backup**: Previous day's log uploaded at 00:05 daily
- **Image storage**: Indefinite retention in `images/` directory
- **Log file**: Single `app.log` file, rotated manually as needed

### MQTT Message Format

**Published Topics** (values as strings):
- Temperature: `"22.50"` (Celsius)
- Humidity: `"45.00"` (percent)
- Motion state: `"0"` or `"1"`
- Camera timestamp: ISO 8601 string

**Subscribed Topics** (commands):
- Light control: `"0"` or `"1"`
- Fan control: `"0"` or `"1"`
- System mode: `"Home"`, `"Away"`, or `"Night"`

## Known Limitations

1. **DHT11 Sensor Accuracy**: ±2°C temperature, ±5% humidity. Readings can fail intermittently.
2. **Motion Debounce**: 30-second cooldown prevents repeated alerts for continuous motion.
3. **Camera Delay**: 2-second warmup time on startup; image capture may take 1-2 seconds.
4. **MQTT Reliability**: No persistent session; messages sent while disconnected are lost.
5. **Cloud Backup Authentication**: Requires manual browser authentication on first run.
6. **Storage Limitations**: No automatic cleanup of old images or CSV files.
7. **Single Instance**: System assumes only one instance running; multiple instances will conflict.
8. **Network Dependency**: All remote control requires active internet connection.
9. **PIR Sensor Limitations**: Cannot distinguish between humans, pets, or other moving objects.
10. **No Encryption**: Local CSV files and images are stored unencrypted.

## Future Work

### Potentail Enhancements

- [ ] **Web Dashboard**: Local Flask/React dashboard for system control
- [ ] **Email/SMS Alerts**: Send notifications via Twilio or SendGrid
- [ ] **Face Recognition**: Distinguish between household members and intruders
- [ ] **Advanced Scheduling**: Time-based automation rules
- [ ] **Database Storage**: Replace CSV with SQLite or PostgreSQL
- [ ] **Video Recording**: Capture short video clips instead of still images
- [ ] **Mobile App**: Native iOS/Android application
- [ ] **Multiple Zones**: Support for multiple rooms/areas
- [ ] **Machine Learning**: Anomaly detection for unusual patterns
- [ ] **Voice Control**: Integration with Google Assistant/Alexa
- [ ] **Battery Backup**: UPS integration for power outage resilience
- [ ] **Encrypted Storage**: Encrypt sensitive data at rest
- [ ] **Multi-user Access**: Role-based access control for family members
- [ ] **Smart Home Integration**: MQTT bridge to Home Assistant or OpenHAB

### Potential Hardware Additions

- Door/window contact sensors (magnetic switches)
- Glass break sensors
- Water leak detectors
- Smoke/CO detectors
- Additional cameras for full coverage
- Siren/strobe light for visual alerts
- Door lock control (smart lock integration)

## Troubleshooting

**Camera not working:**
```bash
# Check camera connection
vcgencmd get_camera

# Should show: supported=1 detected=1
```

**DHT11 read errors:**
- Normal to see occasional errors; sensor is retried automatically
- Ensure proper wiring and 10kΩ pull-up resistor if needed

**MQTT connection fails:**
- Verify Adafruit IO credentials in config.json
- Check internet connectivity
- Confirm feed names match exactly

**Permission errors:**
- Run with sudo or add user to gpio group: `sudo usermod -a -G gpio $USER`

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Adafruit IO for cloud platform and MQTT broker
- Raspberry Pi Foundation for excellent documentation
- gpiozero library maintainers
