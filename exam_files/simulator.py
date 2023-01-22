from random import randrange
import pandas as pd
import os
import ujson
from paho.mqtt import client as mqtt_client
import random
import time

class generateList:
    def __init__(self):
        #load data
        path=os.getcwd()+'/exam_files/predictive_maintenance.csv'
        #load a machine randomly
        self.product_ids=pd.read_csv(path)['Product ID']


    def generate(self):
        #generate random values for each product
        rotation_speed=randrange(290,320)
        torque=randrange(290,320)
        tool_wear=randrange(290,320)
        return ujson.dumps({"product":self.product_ids[randrange(0,len(self.product_ids))],
        'air_temp':randrange(290,320),
        'process_temp':randrange(305,340),'rotation_speed':randrange(1100,2900),
        'torque':randrange(3,76),'tool_wear':randrange(0,255),"target":randrange(0,1)})


class mqttSender:
    def __init__(self):
                # MQTT Server Parameters
        self.client = "exam_big_data"
        self.broker    = "broker-cn.emqx.io"
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.topic     = "exam_big_data"
        self.port=1883

    def connect_mqtt(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)
        # Set Connecting Client ID
        client = mqtt_client.Client(self.client_id)
        #client.username_pw_set(username, password)
        client.on_connect = on_connect
        client.connect(self.broker, self.port)
        return client

    def publish(self,client):
        data=generateList()
        count=1
        while True:
            time.sleep(2)
            result = client.publish(self.topic, data.generate())
            if result[0] != 0:
                print(f"Failed to send")
            else:
                print("record N "+str(count)+" is sent")
                count+=1
    @staticmethod
    def sendValues():
        mqttSender().publish(mqttSender().connect_mqtt())

