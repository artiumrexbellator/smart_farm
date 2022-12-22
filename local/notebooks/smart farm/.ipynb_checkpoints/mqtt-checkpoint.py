from pyspark import SparkContext, SparkConf
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from py4j.protocol import Py4JJavaError

from pyspark.storagelevel import StorageLevel
from pyspark.serializers import UTF8Deserializer
from pyspark.streaming import DStream
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import ujson

#token = os.environ.get("INFLUXDB_TOKEN")
token="3QPbU10kNJS2xjKHzcrdHbwAPzO1myWWQP30ajELJ8L7Gqtb5H08boXXTIJIb8MeEGP9NIlC1N-r9GOiMd6qwQ=="
org = "mustapha"
url = "https://europe-west1-1.gcp.cloud2.influxdata.com"
bucket="farm"

print('ssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssssss')
print(token)
client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

__all__ = ['MQTTUtils']


class MQTTUtils(object):

    @staticmethod
    def createStream(ssc, brokerUrl, topic,
                     storageLevel=StorageLevel.MEMORY_AND_DISK_SER_2):
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


def printHistogram(time, rdd):
    c = rdd.collect()
    print("***************************************")
    for row in c:
        if len(row) > 0 :
            streamData=ujson.loads(row)
            write_api.write(bucket=bucket, record=[{"measurement":"temperature_humidity","time": time,"fields": {
                "temperature":streamData['temp'],
                "humidity": streamData['humidity']
            }}])
            print("record saved to influxDb")

conf=SparkConf()
conf.setMaster('spark://spark-master:7077')

sc = SparkContext.getOrCreate(conf)
ssc=StreamingContext(sc,1)
ds=MQTTUtils.createStream(ssc,"tcp://test.mosquitto.org:1883","dht2022")

data = ds.transform(lambda rdd: rdd.sortByKey())
data.foreachRDD(printHistogram)

ssc.start()
ssc.awaitTermination()