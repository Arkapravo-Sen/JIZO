# Importing Libraries
import RPi.GPIO as GPIO  # Library for Raspberry Pi GPIO
import time  # Time-related functions
import ssl  # SSL library for secure connections
import smtplib  # SMTP library for email sending
import cv2  # OpenCV for computer vision
import pyaudio  # PyAudio for audio input/output
import numpy as np  # Numpy for numerical operations
import Adafruit_DHT  # Adafruit library for DHT sensors
import Adafruit_ADS1x15  # Adafruit library for ADC

# Set Up Email
# Setup port no. and server name
smtp_port = 587
smtp_server = "smtp.gmail.com"

# Your email password
pswd = "Go to your google account and select app passwords / less secure apps. Put in the password google gives to you here."

# Create SSL context
simple_email_context = ssl.create_default_context()

# Function to send email
def Send_Message_To_Receiver(sender, receiver, message):
    try:
        print("Connecting to Server ...")
        # Connect to SMTP server
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls(context=simple_email_context)
        TIE_server.login(sender, pswd)  # Login to sender's email
        print("Connected to Server")
        print()
        print(f"Sending email to - {receiver}")
        # Send email
        TIE_server.sendmail(sender, receiver, message)
        print(f"Message sent to {receiver}")
    except Exception as e:
        print(e)
    finally:
        TIE_server.quit()

# Check for movement
def MOVEMENT_STATUS(GPIO_PIN_IN):
    if GPIO.input(GPIO_PIN_IN):
        MOVE_FLAG = True
        return MOVE_FLAG
    else:
        MOVE_FLAG = False
        return MOVE_FLAG

# Check for person
def PERSON_STATUS():
    # Load YOLO model for object detection
    net = cv2.dnn.readNet("/home/raspberrypi/dnn_model-220107-114215/dnn_model/yolov4-tiny.weights", "/home/raspberrypi/dnn_model-220107-114215/dnn_model/yolov4-tiny.cfg")
    model = cv2.dnn_DetectionModel(net)
    model.setInputParams(size=(150, 150), scale=1/255)

    # Initialize Camera
    cap = cv2.VideoCapture(0)
    
    while True:
        class_id = -1
        # Get Frames
        ret, frame = cap.read()
        
        # Object Detection
        (class_ids, score, bboxes) = model.detect(frame)
        for class_id, score, bbox in zip(class_ids, score, bboxes):
            (x, y, w, h) = bbox
            cv2.putText(frame, str(class_id), (x, y - 5), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 255, 255), 3)
        
        cv2.waitKey(1)
        return class_id

# Check temperature
def Check_Temperature(sensor, pin):
    try:
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        temp_F = temperature * 9 / 5 + 32  # Convert to Fahrenheit
        return temp_F
    except KeyboardInterrupt:
        print('Stopped Temperature Check')
    except Exception as e:
        print(f"An Error Occurred {e}")
        time.sleep(2)

# Checking voltage
# Create an ADS1115 instance
ads = Adafruit_ADS1x15.ADS1115()

# Function to read voltage
def READ_VOLTAGE(adc_channel):
    # Read the ADC value
    adc_value = ads.read_adc(adc_channel, gain=2/3)
    # Calculate voltage
    voltage = adc_value * 6.144 / 32767.0
    return voltage

# Function to start timer
def start_time():
    start = time.time()
    return start
