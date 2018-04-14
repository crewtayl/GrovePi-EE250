#after you `pip3 install paho-mqtt`, you can import the library successfully
import paho.mqtt.client as mqtt
import time
light_on = 0
led = 3
dht_sensor_port = 0
"""It is often best to read code starting from __main__ and reading the function 
definitions as they show up in the code. This will help you understand the
function defintions since you get a little more context. Jump to the __main__
portion of this code and start reading!"""

#Custom callbacks need to be structured with three args like on_message()
def light_callback(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    global light_on
    global led
    if(light_on):
        grovpi.digitalWrite(led, 0)
        light_on = 0
    else:
        grovepi.digitalWrite(led, 1)
        light_on = 1
def message_callback(client, userdata, message):
    #the third argument is 'message' here unlike 'msg' in on_message 
    print(message.payload)
"""Since we attached this function to the mqtt client below, this function 
(or "callback") will be executed when this client receives a CONNACK (i.e., 
a connection acknowledgement packet) response from the server. """
def on_connect(client, userdata, flags, rc):
    print("Connected to server (i.e., broker) with result code "+str(rc))

    """Once our client has successfully conected, it makes sense to subscribe to
    all the topics of interest. Also, subscribing in on_connect() means that, 
    if we lose the connection and the library reconnects for us, this callback
    will be called again thus renewing the subscriptions. Simply subscribing
    to a topic will default to messages received on said topic triggering the 
    callback attached to client.on_message, which we assigned below in __main__.
    """
    client.subscribe("anrg-pi2/light")
    #You can also add a custom callback to specific topics. First, you need to
    #subscribe to the topic. Then, add the callback.
    client.subscribe("anrg-pi0/message")
    client.message_callback_add("anrg-pi2/light", light_callback)
    client.message_callback_add("anrg-pi2/message", message_callback)


"""This object (functions are objects!) serves as the default callback for 
messages received when another node publishes a message this client is 
subscribed to. By "default,"" we mean that this callback is called if a custom 
callback has not been registered using paho-mqtt's message_callback_add()."""
def on_message(client, userdata, msg):
    """The paho-mqtt library typically converts message payloads into a *byte* 
    string before a message is sent, even if you send an int or a float. Python
    will not convert the payload into a string for printing, so you will have
    to convert it manually. Yes, a *byte* string is different from a string in
    python! Python's approach to strings is very different from C/C++. You'll 
    have to look this one up on your own to better understand python strings."""
    print("on_message: " + msg.topic + " " + str(msg.payload, "utf-8"))
    print("on_message: msg.payload is of type " + str(type(msg.payload)))


# If you do not remember what this if statement is for, look in lab04/part1.
if __name__ == '__main__':
    #create a client object
    client = mqtt.Client()
    global dht_sensor_port
    #attach a default callback which we defined above for incoming mqtt messages
    client.on_message = on_message

    #attach the on_connect() callback function defined above to the mqtt client
    client.on_connect = on_connect

    """Connect using the following hostname, port, and keepalive interval (in 
    seconds). We added "host=", "port=", and "keepalive=" for illustrative 
    pourposes. You can omit this in python. For example:
    
    `client.connect("eclipse.usc.edu", 11000, 60)` 
    
    The keepalive interval indicates when to send keepalive packets to the 
    server in the event no messages have been published from or sent to this 
    client. If the connection request is successful, the callback attached to
    `client.on_connect` will be called."""
    client.connect(host="eclipse.usc.edu", port=11000, keepalive=60)

    """In our prior labs, we did not use multiple threads per se. Instead, we
    wrote clients and servers all in separate *processes*. However, every 
    program with networking involved generally requires multiple threads to
    make coding simpler. Using MQTT is no different. If you are doing nothing 
    in this thread, you can run 
    
    `client.loop_forever()`
    
    which will block forever. This function processes network traffic (socket 
    programming is used under the hood), dispatches callbacks, and handles 
    reconnecting. However, we do want to use this thread so we'll use the 
    following line which will ask paho-mqtt to spawn a separate thread to handle
    incoming and outgoing mqtt messages."""
    client.loop_start()
    #Since the library will take care of things in the background, we can use
    #this thread to regularly publish messages.
    time.sleep(1)
    while (True):
            [temp,hum] = grovepi.dht(dht_sensor_port,1)
            #publish a float
            client.publish("anrg-pi2/temperature", temp)
            client.publish("anrg-pi2/humidity", hum)
        time.sleep(1)

    #When you run this program, why do you see the float message first?