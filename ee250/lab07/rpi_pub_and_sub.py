"""EE 250L Lab 07 Skeleton Code

Run rpi_pub_and_sub.py on your Raspberry Pi."""

import paho.mqtt.client as mqtt
from grove_rgb_lcd import *
import time
def lcd_callback(client, userdata, message):
    setRGB(0,255,0)
    setText(message)
    #the third argument is 'message' here unlike 'msg' in on_message 
    
def led_callback(client, userdata, message):
    led = 2
    if message == "LED_ON":
        print("LEDON")
        digitalWrite(led,1) 
    if message == "LED_OFF":
        print("LEDOFF")
        digitalWrite(led,0)
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))
    client.subscribe("anrg-pi2/lcd")
    client.subscribe("anrg-pi2/led")
    client.message_callback_add("anrg-pi2/lcd", lcd_callback)
    client.message_callback_add("anrg-pi2/led", led_callback)
    #subscribe to topics of interest here

#Default message callback. Please use custom callbacks.
def on_message(client, userdata, msg):
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))

if __name__ == '__main__':
    button = 8
    ultrasonic_ranger = 3
    grovepi.pinMode(button,"INPUT")
    #this section is covered in publisher_and_subscriber_example.py
    client = mqtt.Client()
    client.on_message = on_message
    client.on_connect = on_connect
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)
    client.loop_start()

    while True:
        if grovepi.digitalRead(button):
            client.publish("anrg-pi2/button", "Button pressed!")
        client.publish("anrg-pi2/ultrasonic", ultrasonicRead(ultrasonic_ranger))