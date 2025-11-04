from gpiozero import MotionSensor
import time

# Create an object for the PIR sensor, specifying the GPIO pin it's connected to.
pir = MotionSensor(17)

print("PIR Module Test (CTRL+C to exit)")
time.sleep(2)
print("Ready")

try:
    while True:
        # The wait_for_motion() method will block the script until motion is detected.
        pir.wait_for_motion()
        print("Motion detected!")

        # The wait_for_no_motion() method will block the script until motion has stopped.
        pir.wait_for_no_motion()
        print("Motion stopped!")

except KeyboardInterrupt:
    print("Exiting...")
