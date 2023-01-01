import sys
import operator

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from mqtt import MQTTUtils

conf=SparkConf()
conf.setMaster('spark://spark-master:7077')

sc = SparkContext.getOrCreate(conf)
ssc = StreamingContext(sc, 1)
ssc.checkpoint("checkpoint")

# broker URI
brokerUrl = "tcp://test.mosquitto.org:1883" # "tcp://iot.eclipse.org:1883"
# topic or topic pattern where temperature data is being sent
topic = "wokwi-dht1"

mqttStream = MQTTUtils.createStream(ssc, brokerUrl, topic,username=None, password=None)

counts = mqttStream.transform(lambda rdd: rdd.sortByKey())


def printHistogram(time, rdd):
    c = rdd.collect()
    print("-------------------------------------------")
    print("Time: %s" % time)
    print("-------------------------------------------")
    for record in c:
    	# "draw" our lil' ASCII-based histogram
        print(str(record[0]) + ': ' + '#'*record[1])
    print("")

counts.foreachRDD(printHistogram)

ssc.start()
ssc.awaitTermination()