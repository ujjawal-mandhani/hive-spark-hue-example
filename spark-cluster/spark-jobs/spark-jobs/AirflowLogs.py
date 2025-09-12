# pyspark --conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
    # --conf spark.sql.catalog.hudi=org.apache.spark.sql.hudi.catalog.HoodieCatalog \
    # --conf spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension \
    # --conf spark.sql.catalog.spark_catalog.type=hive \
    # --conf spark.sql.catalog.spark_catalog.uri=thrift://metastore:9083
# spark-submit --conf spark.serializer=org.apache.spark.serializer.KryoSerializer \
#     --conf spark.sql.catalog.hudi=org.apache.spark.sql.hudi.catalog.HoodieCatalog \
#     --conf spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension \
#     --conf spark.sql.catalog.spark_catalog.type=hive \
#     --conf spark.sql.catalog.spark_catalog.uri=thrift://metastore:9083 AirflowLogs.py '{"incremental": "Y"}'

from pyspark.sql.functions import *
from pyspark.sql import SparkSession
import sys
import json

spark = SparkSession.builder.getOrCreate()
spark.sparkContext.setLogLevel("WARN")

spark_configs = json.loads(sys.argv[1])


df = spark.read.json("hdfs:///user/airflow_logs/celery_celery-worker-1")
# namenode:8020
df_exploded = spark.sql("""
    select
        chan,
        detail.detail.current_state as current_state,
        detail.detail.message as message,
        detail.detail.reason as reason,
        error_detail
        event,
        level,
        logger,
        ti,
        timestamp,
        split(replace(input_file_name(), '_____', '/'), '/')[5] as host_name,
        replace(split(replace(input_file_name(), '_____', '/'), '/')[6], 'dag_id=', '') as dag_id,
        replace(split(replace(input_file_name(), '_____', '/'), '/')[7], 'run_id=', '') as run_id,
        replace(split(replace(input_file_name(), '_____', '/'), '/')[8], 'task_id=', '') as task_id,
        input_file_name() as hdfs_file_name
    from {df}
""", df=df)
# df_exploded.filter("dag_id!='torrent_scrapper_dag'").show(10, False)
# spark.sql("""
#     select  dag_id, run_id, task_id, timestamp, count(1) as cnt
#     from {df_exploded}        
#     group by dag_id, run_id, task_id, timestamp  
#     having count(1) > 1
# """, df_exploded=df_exploded).show(10, False)

hudi_options = {
    "hoodie.table.name": "hudi_table_airflow_logs",
    "hoodie.datasource.write.recordkey.field": "dag_id,run_id,task_id,timestamp",
    "hoodie.datasource.write.partitionpath.field": "",
    "hoodie.datasource.write.precombine.field": "timestamp",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",  # or MERGE_ON_READ
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.mode": "hms",
    "hoodie.datasource.hive_sync.metastore.uris": "thrift://metastore:9083",
    "hoodie.datasource.hive_sync.database": "airflow_dbt",
    "hoodie.datasource.hive_sync.table": "hudi_table_airflow_logs",
    "hoodie.datasource.hive_sync.support_timestamp": "true",
    "hoodie.metrics.on": "false",
    "hoodie.datasource.write.hive_sync.enable": "true",
    # "hoodie.datasource.hive_sync.jdbcurl": "jdbc:hive2://spark-master:10000/airflow_dbt"
    
}

if spark_configs.get("incremental", 'N') == "Y":
    mode = "overwrite"
    df_final = df_exploded
else:
    mode = "append"
    df_hudi = spark.read.format("hudi").load("hdfs:///user/airflow_logs/transformed/celery_celery_worker_1")
    # namenode:8020
    df_final = spark.sql("""
        with distinct_hudi_file_name as (
            select distinct hdfs_file_name from {df_hudi}
        ),
        distinct_exploded_file_name as (
            select distinct hdfs_file_name from {df_exploded}
        ),
        final_blck as (    
            select distinct A.hdfs_file_name 
            from distinct_exploded_file_name A
            left join distinct_hudi_file_name B
            on A.hdfs_file_name = B.hdfs_file_name 
            where B.hdfs_file_name is null
        )
        select * from {df_exploded} A
        join final_blck B 
        on A.hdfs_file_name = B.hdfs_file_name
    """, df_hudi=df_hudi, df_exploded=df_exploded)

if df_final.take(1) != []:
    df_final.write.format("hudi") \
        .options(**hudi_options) \
        .mode(mode) \
        .save("hdfs://namenode:8020/user/airflow_logs/transformed/celery_celery_worker_1")
        # namenode:8020
    