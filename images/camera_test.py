import os
import time
from picamera2 import Picamera2

# The name of the file we want to save
image_filename = "test_image.jpg"

# --- Image Capture ---
try:
    # Initialize the camera
    picam2 = Picamera2()
    
    # Configure the camera for still capture
    config = picam2.create_still_configuration()
    picam2.configure(config)
    
    # Start the camera preview (optional, but good for setup)
    picam2.start()
    time.sleep(2) # Give the camera time to adjust to light levels
    
    # Capture and save the image
    picam2.capture_file(image_filename)
    print(f"Capture command sent. Attempting to save as {image_filename}")
    
    # Stop the camera
    picam2.stop()

except Exception as e:
    print(f"An error occurred with the camera: {e}")

# --- Verification ---
# Check if the file was created and is not empty
# os.path.exists() checks for the file.
# os.path.getsize() checks the file size in bytes. A size > 0 means it's not empty.
if os.path.exists(image_filename) and os.path.getsize(image_filename) > 0:
    print(f"SUCCESS: Image '{image_filename}' was captured and saved.")
else:
    print(f"FAILURE: Image '{image_filename}' was not created or is empty.")
