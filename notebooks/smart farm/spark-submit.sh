# Submit Python code to SparkMaster

PYTHON_JOB=$1

if [ -z $2 ]
then
	EXEC_MEM="512M"
else
	EXEC_MEM=$2
fi

spark-submit --master spark://spark-master:7077 --num-executors 3 \
	     --executor-memory 1024M --executor-cores 1 \
             --packages org.apache.bahir:spark-streaming-mqtt_2.11:2.4.0 \
             $PYTHON_JOB mqtt.py

