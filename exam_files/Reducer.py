from simulator import mqttSender
import time
from datetime import datetime
import influxdb_client
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from logistic_regression import machinesLogreg
import ujson

token="vy_f7_RxMP9PjXKchZUe-cIm5g7EDdi7ZgMLtL2PoWst1kx-jcdkZ_x2vBKbQ5GR8hFaq5F2AQrGU_CZwa53vQ=="
org = "mustapha"
url = "https://europe-west1-1.gcp.cloud2.influxdata.com"
bucket="exam"

#influxDb
influx_client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

#logistic regression model
model=machinesLogreg()

def subscribe(client,topic,influxClient,write_api):
    def on_message(client, userdata, msg):
        msg=ujson.loads(msg.payload.decode())
        #predict failure
        msg["prediction"]=model.predict([[msg['air_temp'],msg['process_temp'],msg['rotation_speed'],msg['torque'],msg['tool_wear']]])[0]
        write_api.write(bucket=bucket, record=[{"measurement":'machines',"fields": {
                    "product":msg["product"],
                    "air_temp":msg["air_temp"],
                    "process_temp":msg["process_temp"],
                    "rotation_speed":msg["rotation_speed"],
                    "torque":msg["torque"],
                    "tool_wear":msg["tool_wear"],
                    "target":msg["target"],
                    "prediction":msg['prediction']
                }}])
        print(f"saved `{msg}")
    client.subscribe(topic)
    client.on_message = on_message

mqtt=mqttSender().connect_mqtt()

subscribe(mqtt,"exam_big_data", influx_client, write_api)
mqtt.loop_forever()
