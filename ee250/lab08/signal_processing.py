import paho.mqtt.client as mqtt
import time
import requests
import json
from datetime import datetime

# MQTT variables
broker_hostname = "eclipse.usc.edu"
broker_port = 11000
ultrasonic_ranger1_topic = "ultrasonic_ranger1"
ultrasonic_ranger2_topic = "ultrasonic_ranger2"

# Lists holding the ultrasonic ranger sensor distance readings. Change the 
# value of MAX_LIST_LENGTH depending on how many distance samples you would 
# like to keep at any point in time.
MAX_LIST_LENGTH = 10
ranger1_dist = [90] * MAX_LIST_LENGTH
ranger2_dist = [90] * MAX_LIST_LENGTH
ranger1_dist_avg = [90] * MAX_LIST_LENGTH
ranger2_dist_avg = [90] * MAX_LIST_LENGTH
ranger1_dist_avg_difference = [0] * MAX_LIST_LENGTH
ranger2_dist_avg_difference = [0] * MAX_LIST_LENGTH

def ranger1_callback(client, userdata, msg):
    global ranger1_dist
    global ranger1_dist_avg
    global ranger1_dist_avg_difference
    if int(msg.payload) < 150:
        ranger1_dist.append(int(msg.payload))
        sum_of_ranger1 = 0
        for x in range(MAX_LIST_LENGTH):
            sum_of_ranger1 = sum_of_ranger1 + ranger1_dist[x]
        ranger1_dist_avg.append(sum_of_ranger1 / MAX_LIST_LENGTH)
        ranger1_dist_avg_difference.append(int(ranger1_dist_avg[MAX_LIST_LENGTH]) - int(ranger1_dist_avg[MAX_LIST_LENGTH - 1]))
        ranger1_dist_avg = ranger1_dist_avg[-MAX_LIST_LENGTH:]
        ranger1_dist_avg_difference = ranger1_dist_avg_difference[-MAX_LIST_LENGTH:]
        ranger1_dist = ranger1_dist[-MAX_LIST_LENGTH:]

def ranger2_callback(client, userdata, msg):
    global ranger2_dist
    global ranger2_dist_avg
    global ranger2_dist_avg_difference
    if int(msg.payload) < 125:
        ranger2_dist.append(int(msg.payload))
        sum_of_ranger2 = 0
        for x in range(MAX_LIST_LENGTH):
            sum_of_ranger2 = sum_of_ranger2 + ranger2_dist[x]
        ranger2_dist_avg.append(sum_of_ranger2 / MAX_LIST_LENGTH)
        ranger2_dist_avg_difference.append(int(ranger2_dist_avg[MAX_LIST_LENGTH]) - int(ranger2_dist_avg[MAX_LIST_LENGTH - 1]))
        ranger2_dist_avg = ranger2_dist_avg[-MAX_LIST_LENGTH:]
        ranger2_dist_avg = ranger2_dist_avg[-MAX_LIST_LENGTH:]
        ranger2_dist_avg_difference = ranger2_dist_avg_difference[-MAX_LIST_LENGTH:]
        ranger2_dist = ranger2_dist[-MAX_LIST_LENGTH:]

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(ultrasonic_ranger1_topic)
    client.message_callback_add(ultrasonic_ranger1_topic, ranger1_callback)
    client.subscribe(ultrasonic_ranger2_topic)
    client.message_callback_add(ultrasonic_ranger2_topic, ranger2_callback)

# The callback for when a PUBLISH message is received from the server.
# This should not be called.
def on_message(client, userdata, msg): 
    print(msg.topic + " " + str(msg.payload))

if __name__ == '__main__':
    # Connect to broker and start loop    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_hostname, broker_port, 60)
    client.loop_start()
    global ranger2_dist_avg_difference
    global ranger1_dist_avg_difference
    prev_sum_of_ranger1_diff = 0
    prev_sum_of_ranger2_diff = 0
    wasStillLeft = 0
    wasStillRight = 0
    goMiddle = 1
    hdr = {
        'Content-Type': 'application/json',
        'Authorization': None #not using HTTP secure
    }

    # The payload of our message starts as a simple dictionary. Before sending
    # the HTTP message, we will format this into a json object
    
    while True:
        """ You have two lists, ranger1_dist and ranger2_dist, which hold a window
        of the past MAX_LIST_LENGTH samples published by ultrasonic ranger 1
        and 2, respectively. The signals are published roughly at intervals of
        200ms, or 5 samples/second (5 Hz). The values published are the 
        distances in centimeters to the closest object. Expect values between 
        0 and 512. However, these rangers do not detect people well beyond 
        ~125cm. """
        
        # TODO: detect movement and/or position
        sum_of_ranger1_dif = 0
        sum_of_ranger2_dif = 0
        payload = ""
        for x in range(MAX_LIST_LENGTH):
            sum_of_ranger2_dif += ranger2_dist_avg_difference[x]
            sum_of_ranger1_dif += ranger1_dist_avg_difference[x]

        if sum_of_ranger2_dif == prev_sum_of_ranger2_diff and ranger1_dist[MAX_LIST_LENGTH - 1] < 55:
                print("Still Left")
                payload = "Still - Left"
                wasStillLeft = 1
        elif sum_of_ranger1_dif > prev_sum_of_ranger1_diff and (sum_of_ranger2_dif == prev_sum_of_ranger2_diff):
                print("Moving Right")
                payload = "Moving Right"
                wasStillRight = 0
        elif (sum_of_ranger2_dif > prev_sum_of_ranger2_diff and (sum_of_ranger1_dif == prev_sum_of_ranger1_diff)):
                print("Moving Left")
                payload = "Moving Left"
                wasStillLeft = 0
        elif sum_of_ranger1_dif == prev_sum_of_ranger1_diff and ranger2_dist[MAX_LIST_LENGTH - 1] < 55:
                print("Still Right")
                payload = "Still - Right"
                wasStillRight = 1
        elif abs(sum_of_ranger1_dif) < 3 and abs(sum_of_ranger2_dif < 3) and ranger2_dist[MAX_LIST_LENGTH - 1] > 65 and ranger1_dist[MAX_LIST_LENGTH - 1] > 65 and ranger2_dist[MAX_LIST_LENGTH - 1] < 90 and ranger1_dist[MAX_LIST_LENGTH - 1] < 90:
                print("Still - Middle")
                payload = "Still - Middle"
        # elif sum_of_ranger1_dif == prev_sum_of_ranger1_diff:
        #     if sum_of_ranger2_dif == prev_sum_of_ranger2_diff and goMiddle:
        #         print("Still Middle")
        #         goMiddle = 0
        if payload:
            payload2 = {
                'time': str(datetime.now()),
                'event': payload
                }
            response = requests.post("http://0.0.0.0:5000/post-event", headers = hdr,
                                 data = json.dumps(payload2))
        # print("ranger1: " + str(ranger1_dist[-1:]) + ", ranger2: " + 
        #     str(ranger2_dist[-1:])) 
        # print("ranger1 avg: " + str(ranger1_dist_avg[-1:]) + ", ranger2 avg: " + 
        #     str(ranger2_dist_avg[-1:])) 
        # print("ranger1 difference: " + str(sum(ranger1_dist_avg_difference)) + ", ranger2 difference: " + 
        #     str(sum(ranger2_dist_avg_difference)))
        prev_sum_of_ranger1_diff = sum_of_ranger1_dif
        prev_sum_of_ranger2_diff = sum_of_ranger2_dif
        time.sleep(0.05)