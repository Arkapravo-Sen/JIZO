import MYLIBRARY as L  # Import your custom library as L
import RPi.GPIO as GPIO  # Library for Raspberry Pi GPIO
import time  # Time-related functions
import cv2  # OpenCV for computer vision
import pyaudio  # PyAudio for audio input/output
import numpy as np  # Numpy for numerical operations
import Adafruit_DHT  # Adafruit library for DHT sensors
import json  # JSON handling
import smtplib  # SMTP library for email sending
import ssl  # SSL library for secure connections

# Wait for 10 seconds to allow for system initialization
time.sleep(10)

# Set GPIO mode and pin configurations
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN)  # Input pin for voltage monitoring
GPIO.setup(17, GPIO.OUT)  # Output pin for GPIO operation
GPIO.setup(26, GPIO.OUT)  # Output pin for fan control

# Print status message
print("Check for Voltage")

# Pause time between loops
pause = 3

# Counter for tracking occurrences
counter = 0

# Flags to track various conditions
VOLT_TAG = False
Person_Tag = False
Noise_Tag = False
Temp_Tag = False

# Set initial state of GPIO pin
GPIO.output(26, 0)

# Main loop
while True:
    # Voltage monitoring loop
    volt_buffer = 0
    while True:
        time.sleep(1)
        volts = L.READ_VOLTAGE(3)  # Read voltage from custom library

        if volts >= 4.90:
            print("Car is on, do nothing", volts)
            VOLT_TAG = True
            counter = 0
        else:
            print("Car stopped", volts)
            volt_buffer += 1
            if volt_buffer >= 5:
                VOLT_TAG = False
                break

    time.sleep(3)

    # Person detection loop
    while True:
        PERSON_FLAG = L.PERSON_STATUS()  # Check person presence using custom library

        if PERSON_FLAG == 0:
            Person_Tag = True
            print("Person Detected")
            cv2.destroyAllWindows()  # Close any open CV windows
            break
        else:
            print("Person Not Detected")
            cv2.destroyAllWindows()  # Close any open CV windows
            break

    time.sleep(3)

    # If person is not detected, listen for noise
    if Person_Tag == False:
        # PyAudio setup
        p = pyaudio.PyAudio()
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100

        # Start time for noise detection
        start_time = L.start_time()
        max_duration = 20  # Maximum duration for noise detection

        # Open audio stream for noise detection
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print("Listening for noise...")

        # Noise detection loop
        while True:
            audio_data = np.frombuffer(stream.read(CHUNK), dtype=np.int16)

            if np.max(np.abs(audio_data)) > 1000:
                print("Noise detected")
                Noise_Tag = True
                break

            if (time.time() - start_time) >= max_duration:
                print("No noise detected, max duration reached")
                Noise_Tag = False
                break

        # Close audio stream
        stream.stop_stream()
        stream.close()
        p.terminate()

        time.sleep(3)

    # If noise or person detected and car not off, check temperature
    if (Noise_Tag == True or Person_Tag == True) and VOLT_TAG == False:
        VOLT_TAG = False
        Person_Tag = False
        Noise_Tag = False
        counter += 1

        # Read temperature using DHT sensor
        temps = L.Check_Temperature(Adafruit_DHT.DHT11, 27)
        print(temps)
        time.sleep(3)

        # If temperature exceeds threshold, turn on fan
        if temps >= 60:
            GPIO.output(26, 1)  # Turn on fan

    else:
        GPIO.output(26, 0)  # Turn off fan
        counter = 0

    # If conditions trigger alert, send email
    if counter == 1:
        # Read email information from JSON file
        json_file = open('/home/raspberrypi/registered_information.json', 'r')
        json_Data = json_file.read()

        json_obj = json.loads(json_Data)

        emails = json_obj['emergencyEmail']
        sender = json_obj['registeredEmail']
        carNum = json_obj['carNumber']
        subject = 'Someone may be unattended in your Car'
        message = f'Subject: {subject} \n\n WARNING someone is still in your car {carNum}. Please check to make sure everything is ok.'

        # Send alert emails
        for i in range(len(emails)):
            receiver = emails[i].get('email')

            L.Send_Message_To_Receiver(sender, receiver, message)

        # Reset counter
        counter = 0

    # Print status message
    print("Ended Program, Going Again")
    print("Check for Voltage")

    # Pause before next loop iteration
    time.sleep(10)
