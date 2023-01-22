from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from py4j.protocol import Py4JJavaError
import threading

from pyspark.storagelevel import StorageLevel
from pyspark.serializers import UTF8Deserializer
from pyspark.streaming import DStream
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import ujson

#token = os.environ.get("INFLUXDB_TOKEN")
token="vy_f7_RxMP9PjXKchZUe-cIm5g7EDdi7ZgMLtL2PoWst1kx-jcdkZ_x2vBKbQ5GR8hFaq5F2AQrGU_CZwa53vQ=="
org = "mustapha"
url = "https://europe-west1-1.gcp.cloud2.influxdata.com"
bucket="farm"

client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

__all__ = ['MQTTUtils']


class MQTTUtils(object):

    @staticmethod
    def createStream(ssc, brokerUrl, topic,
                     storageLevel=StorageLevel.MEMORY_AND_DISK_SER_2,username="",password="",keepAlive=400):
        """
        Create an input stream that pulls messages from a Mqtt Broker.

        :param ssc:  StreamingContext object
        :param brokerUrl:  Url of remote mqtt publisher
        :param topic:  topic name to subscribe to
        :param storageLevel:  RDD storage level.
        :return: A DStream object
        """
        jlevel = ssc._sc._getJavaStorageLevel(storageLevel)

        try:
            helperClass = ssc._jvm.java.lang.Thread.currentThread().getContextClassLoader() \
                    .loadClass("org.apache.spark.streaming.mqtt.MQTTUtilsPythonHelper")
            helper = helperClass.newInstance()
            jstream = helper.createStream(ssc._jssc, brokerUrl, topic, jlevel)
        except Py4JJavaError as e:
            if 'ClassNotFoundException' in str(e.java_exception):
                MQTTUtils._printErrorMsg(ssc.sparkContext)
            raise e

        return DStream(jstream, ssc, UTF8Deserializer())

    @staticmethod
    def _printErrorMsg(sc):
        print("")


def save_data(time, rdd):
    c = rdd.collect()
    for row in c:
        if len(row) > 0 :
            try:
                streamData=ujson.loads(row)
                write_api.write(bucket=bucket, record=[{"measurement":'machines',"time": time,"fields": {
                    "product":streamData["product"],
                    "air_temp":streamData["air_temp"],
                    "process_temp":streamData["process_temp"],
                    "rotation_speed":streamData["rotation_speed"],
                    "torque":streamData["torque"],
                    "tool_wear":streamData["tool_wear"],
                    "targets":streamData['target']
                }}])
                print("saved to influxDb")
            except:
                continue

conf=SparkConf()
conf.setMaster('spark://spark-master:7077')

sc = SparkContext.getOrCreate(conf)
sc.setLogLevel('WARN')

ssc=StreamingContext(sc,1)
dStream=MQTTUtils.createStream(ssc,"tcp://broker-cn.emqx.io:1883","exam_big_data")

dStream.foreachRDD(save_data)


ssc.start()
ssc.awaitTermination()