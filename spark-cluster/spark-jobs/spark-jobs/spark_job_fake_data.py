# pyspark --master yarn \
# --conf spark.serializer=org.apache.spark.serializer.KryoSerializer  \
# --conf spark.sql.catalog.hudi=org.apache.spark.sql.hudi.catalog.HoodieCatalog  \
# --conf spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension  \
# --conf spark.sql.catalog.spark_catalog.type=hive  \
# --conf spark.sql.catalog.spark_catalog.uri=thrift://metastore:9083  \
# --conf spark.eventLog.enabled=true  \
# --conf spark.eventLog.dir=hdfs://namenode:8020/user/airflow/spark-logs \
# --executor-memory 2G \
# --executor-cores 2 \
# --num-executors 3 \
# --driver-memory 2G \
# --conf spark.yarn.am.memory=1G 
# '{"incremental": "Y"}'
# df = spark.read.format("hudi") \
#     .option("hoodie.datasource.query.type", "incremental") \
#     .option("hoodie.datasource.read.begin.instanttime", "000") \
#     .load("hdfs://namenode:8020/user/fake_data/transformed/hudi_table_fake_indian_data")
    
# df = spark.read.parquet("hdfs://namenode:8020/user/fake_data/transformed/hudi_table_fake_indian_data")
# spark.sql("""
#  select id from 
#  {df}
#  group by id having count(1) > 1
#  limit 10
# """, df=df).show(10, False)
import json
import sys
from pyspark.sql.functions import *
from pyspark.sql import SparkSession
from pyspark.sql.window import Window


spark = SparkSession.builder.appName("Fake Data Analysis").getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", 400)
df_indian_data = spark.read.json("hdfs:///user/fake_data/indian_user_data").withColumn("hdfs_file_name", expr("input_file_name()"))

# df.rdd.getNumPartitions()
# spark.conf.get("spark.sql.adaptive.enabled")
# spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
spark_configs = json.loads(sys.argv[1])
incremental_conf = spark_configs.get("incremental", 'N')

spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 25 * 1024 * 1024)
df_pincode_master = spark.read.option("header", "true").csv("hdfs://namenode:8020/user/fake_data/pincode_master").select("pincode", "district", "statename").dropDuplicates()
# df_pincode_master.rdd.getNumPartitions()
df_merged = spark.sql("""
    select /*+ BROADCAST(B) */
    A.*, B.district, B.statename
    from {df_indian_data} A 
    left join {df_pincode_master} B 
    on A.pincode = B.pincode
    where B.pincode is not null
""", df_indian_data=df_indian_data, df_pincode_master=df_pincode_master)
windowSpec = Window.partitionBy("id").orderBy(col("timestamp").desc())
df_merged = df_merged.withColumn("rnk", row_number().over(windowSpec)).filter("rnk =1").drop("rnk")
hudi_options = {
    "hoodie.table.name": "hudi_table_fake_indian_data",
    "hoodie.datasource.write.recordkey.field": "id",
    "hoodie.datasource.write.partitionpath.field": "",
    "hoodie.datasource.write.precombine.field": "timestamp",
    "hoodie.datasource.write.table.type": "COPY_ON_WRITE",  # or MERGE_ON_READ
    "hoodie.datasource.write.operation": "upsert",
    "hoodie.datasource.hive_sync.enable": "true",
    "hoodie.datasource.hive_sync.mode": "hms",
    "hoodie.datasource.hive_sync.metastore.uris": "thrift://metastore:9083",
    "hoodie.datasource.hive_sync.database": "airflow_dbt",
    "hoodie.datasource.hive_sync.table": "hudi_table_fake_indian_data",
    "hoodie.datasource.hive_sync.support_timestamp": "true",
    "hoodie.metrics.on": "false",
    "hoodie.datasource.write.hive_sync.enable": "true",
    "hoodie.avro.schema.evolution.enable": "true",
    "hoodie.datasource.write.schema.evolution.enable": "true",
    "hoodie.datasource.hive_sync.alter_schema": "true",
    "hoodie.datasource.hive_sync.reconciling": "true"
    # "hoodie.datasource.hive_sync.jdbcurl": "jdbc:hive2://spark-master:10000/airflow_dbt"
}

if spark_configs.get("incremental", 'N') == "Y":
    mode = "overwrite"
    df_final = df_merged
else:
    mode = "append"
    df_hudi = spark.read.format("hudi").load("hdfs://namenode:8020/user/fake_data/transformed/hudi_table_fake_indian_data")
    df_final = spark.sql("""
        with distinct_hudi_file_name as (
            select distinct hdfs_file_name from {df_hudi}
        ),
        distinct_exploded_file_name as (
            select distinct hdfs_file_name from {df_merged}
        ),
        final_blck as (    
            select distinct A.hdfs_file_name 
            from distinct_exploded_file_name A
            left join distinct_hudi_file_name B
            on A.hdfs_file_name = B.hdfs_file_name 
            where B.hdfs_file_name is null
        )
        select A.* 
        from {df_merged} A
        join final_blck B 
        on A.hdfs_file_name = B.hdfs_file_name
    """, df_hudi=df_hudi, df_merged=df_merged)

df_final = df_final.repartition(10, col("id"))
df_final = df_final.withColumn("amount", expr("cast(amount as string)"))

if df_final.take(1) != []:
    df_final.write.format("hudi") \
            .options(**hudi_options) \
            .mode(mode) \
            .save("hdfs://namenode:8020/user/fake_data/transformed/hudi_table_fake_indian_data")
# spark.sql("""
#     select pincode, district, statename
#     from {df_pincode_master}
#     group by pincode, district, statename
#     having count(1) > 1
#     limit 10
# """, df_pincode_master=df_pincode_master).show(10)

