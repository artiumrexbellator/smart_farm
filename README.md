# Spark and Kafka in Docker Cluster #    
## Spark and Hadoop Configuration and Release Information ##

Spark Version `2.4.5`, Hadoop version is `2.7`, Python version `3.7.3`.

Apache Spark is running in *Standalone Mode* and controls its own master and worker nodes instead of Yarn managing them.     

Apache Spark with Apache Hadoop support is used to allow the cluster to simulate HDFS distributed filesystem using the shared volume `shared-workspace`.

# Build ##
## Quick-Start ##

Ensure that the Docker environment has enough memory allocated:
- Configure a minimum of 4GB in Docker Resources, ideally 8GB   


Build the images with
 ```
 build.sh
 ```     
Create the Docker volumes before starting services:
 ```
 docker volume create --name=hadoop-distributed-file-system
 ```  
Start the cluster with:  
```
docker-compose up --detach
```
Test the cluster using notebook `./local/notebooks/pyspark-notebook-1.ipynb`  
- Use the JupyterLab environment which should now be available on http://localhost:8889/
- More details about the JupyterLab environment are listed below in the *Connect to Cluster via JupyterLab* section.

## Build Overview ##


The following Docker images are created:  
+ `cluster-base` - this provides the shared directory (`/opt/workspace`) for the HDFS simulation.  
+ `spark-base`  - base Apache Spark image to build the Spark Master and Spark Workers on.   
+ `spark-master` - Spark Master that allows Worker nodes to connect via SPARK_MASTER_PORT, also exposes the Spark Master UI web-page (port 8080).  
+ `spark-worker` - multiple Spark Worker containers can be started from this image to form the cluster.    
+ `jupyterlab` -  built on top of the cluster-base with Python and JupyterLab environment with an additional filesystem for storing Jupyter Notebooks and spark-submit scripts.


The cluster is dependent on a shared volume `shared-workspace` that is created during the docker-compose initialisation
```
volumes:
  shared-workspace:
    name: "hadoop-distributed-file-system"
    driver: local
```

Once created, the data in shared-workspace is persistent in the Docker environment.

## Cluster Dependencies ##

*Docker Compose* is used to link all the cluster components together so that an overall running cluster service can be started.  

`docker-compose.yml` initialises a shared cluster volume for the shared filesystem (HDFS simulation) and also maps `./local/notebooks` to a mount point in the JupyterLab Docker container.  

Various other port-mappings and configuration details are set in this configuration file.  Because all the worker nodes need to be referenced at `localhost`, they are mapped to different port numbers (ports 8081 and 8082 for worker 1 and 2).

## Start Cluster ##

```
docker-compose up --detach
```


## Stop Cluster ##
```
docker-compose down
```

### Monitoring the Spark Cluster and Killing Application Jobs ###

View the overall state of the cluster via the *Spark Master Web UI* at `http://localhost:8080/`   

This also lists the URL for the *Spark Master Service*: `spark://spark-master:7077`       
### Spark History Server ###

Access the history server to view complete and incomplete applications on a per node basis.  
To view the node 1 history view `http://localhost:18081` in a web browser  
to view the node 2 history view `http://localhost:18082`  

Spark history logs are written to `/opt/workspace/events` which is on the cluster-wide shared file-system, so each worker-node shows the same history view.  

The Spark History Server is configured by copying `spark-defaults.conf` to the Spark-Home `conf` directory on each worker-node as part of Docker build process (`spark-worker.Dockerfile`).

To clear down the history of jobs, just connect to the spark master or worker node and delete the files created by job executions in `/opt/workspace/events`.

# Connect to Cluster via JupyterLab to run Interactive Notebook Sessions #

Use a web-browser to connect to `http://localhost:8889`   


View the progress and output from the Spark Master console UI:   
http://localhost:8080/  
and the history server (after the job has completed):  
http://localhost:18081/  
(click on the AppID link to drill down into the job execution stats and details of the DAG workflow)  
