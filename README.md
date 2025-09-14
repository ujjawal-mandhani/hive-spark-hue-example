### Required HDFS command

```bash
hdfs dfs -mkdir -p /user/spark/scripts
hdfs dfs -put spark_udf_test.py /user/spark/scripts
hdfs dfs -rm /user/spark/scripts/spark_udf_test.py
```

**Upload required jars**

```bash
hdfs dfs -mkdir -p hdfs://namenode:8020/user/spark/jars/spark-3.5.0/
hdfs dfs -put /usr/local/share/spark/python/lib/py4j-0.10.9.7-src.zip hdfs://namenode:8020/user/spark/jars/spark-3.5.0/
hdfs dfs -put /usr/local/share/spark/python/lib/pyspark.zip hdfs://namenode:8020/user/spark/jars/spark-3.5.0/
hdfs dfs -put $SPARK_HOME/jars/hudi-spark3.5-bundle_2.12-1.0.2.jar hdfs://namenode:8020/user/spark/jars
pyspark --conf spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.catalog.hudi=org.apache.spark.sql.hudi.catalog.HoodieCatalog --conf spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension --conf spark.sql.catalog.spark_catalog.type=hive --conf spark.sql.catalog.spark_catalog.uri=thrift://metastore:9083
hdfs dfs -put $SPARK_HOME/jars/hudi-spark3.5-bundle_2.12-1.0.2.jar hdfs://namenode:8020/user/spark/jars/spark-3.5.0

spark-submit --master yarn --conf spark.yarn.appMasterEnv.PYSPARK_PYTHON=python3 --conf spark.executorEnv.PYSPARK_PYTHON=python3 --conf spark.yarn.dist.files=hdfs://namenode:8020/user/spark/jars/pyspark.zip,hdfs://namenode:8020/user/spark/jars/py4j-0.10.9.9-src.zip --conf spark.serializer=org.apache.spark.serializer.KryoSerializer --conf spark.sql.catalog.hudi=org.apache.spark.sql.hudi.catalog.HoodieCatalog --conf spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension --conf spark.sql.catalog.spark_catalog.type=hive --conf spark.sql.catalog.spark_catalog.uri=thrift://metastore:9083 --conf spark.yarn.am.memory=512m --conf spark.yarn.am.cores=1  --jars hdfs://namenode:8020/user/spark/jars/spark-3.5.0/hudi-spark3.5-bundle_2.12-1.0.2.jar --num-executors 2 --executor-cores 1 --executor-memory 1G --name spark_udf_test --verbose --deploy-mode cluster hdfs://namenode:8020/user/spark/scripts/AirflowLogs.py '{"incremental": "Y"}'
```

![alt text](src/hdfs_ui.png)

### Required Yarn command
yarn application -list -appStates ALL

yarn logs -applicationId <application_id>

![alt text](src/yarn_ui.png)

### spark yarn setup confirmation

dcexec spark-master jps -> DataNode, Master
dcexec spark-worker-1 jps -> Worker, DataNode
dcexec spark-worker-2 jps -> Worker, DataNode
dcexec namenode jps -> NameNode, ResourceManager

Special rule for ThriftServer
Spark hard-codes: “Cluster deploy mode is not applicable to Spark Thrift server.”
So the ThriftServer must be started in client mode; executor containers still run on the worker nodes.
yarn node -list -showDetails
