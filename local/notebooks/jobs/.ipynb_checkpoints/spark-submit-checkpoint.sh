# Submit Python code to SparkMaster

PYTHON_JOB=$1

if [ -z $2 ]
then
	EXEC_MEM="512M"
else
	EXEC_MEM=$2
fi

spark-submit --master spark://spark-master:7077 --num-executors 2 \
	     --executor-memory $EXEC_MEM --executor-cores 1 \
             --packages org.apache.spark:spark-sql-kafka-0-10_2.11:2.4.4 \
             $PYTHON_JOB pi.py

