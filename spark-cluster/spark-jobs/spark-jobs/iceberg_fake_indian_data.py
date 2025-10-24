# pyspark --master yarn \
# --conf spark.serializer=org.apache.spark.serializer.KryoSerializer  \
# --conf spark.sql.catalog.hudi=org.apache.spark.sql.hudi.catalog.HoodieCatalog  \
# --conf spark.sql.extensions=org.apache.spark.sql.hudi.HoodieSparkSessionExtension,org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions  \
# --conf spark.sql.catalog.spark_catalog.type=hive  \
# --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkSessionCatalog \
# --conf spark.sql.catalog.spark_catalog.uri=thrift://metastore:9083  \
# --conf spark.eventLog.enabled=true  \
# --conf spark.eventLog.dir=hdfs://namenode:8020/user/airflow/spark-logs \
# --conf spark.sql.catalog.iceberg=org.apache.iceberg.spark.SparkCatalog \
# --conf spark.sql.catalog.iceberg.type=hive \
# --conf spark.sql.catalog.iceberg.uri=thrift://metastore:9083 \
# --executor-memory 2G \
# --executor-cores 2 \
# --num-executors 3 \
# --driver-memory 2G \
# --conf spark.yarn.am.memory=1G 
# '{"incremental": "Y"}'


import json
import sys
from pyspark.sql.functions import *
from pyspark.sql import SparkSession
from pyspark.sql.window import Window


spark = SparkSession.builder.appName("Fake Data Analysis").getOrCreate()
spark.conf.set("spark.sql.shuffle.partitions", 400)
df_indian_data = spark.read.json("hdfs:///user/fake_data/indian_user_data").withColumn("hdfs_file_name", expr("input_file_name()"))
spark_configs = json.loads(sys.argv[1])
incremental_conf = spark_configs.get("incremental", 'N')

spark.conf.set("spark.sql.autoBroadcastJoinThreshold", 25 * 1024 * 1024)
df_pincode_master = spark.read.option("header", "true").csv("hdfs://namenode:8020/user/fake_data/pincode_master").select("pincode", "district", "statename").dropDuplicates()

df_merged = spark.sql("""
    select /*+ BROADCAST(B) */
    A.*, B.district, B.statename
    from {df_indian_data} A 
    left join {df_pincode_master} B 
    on A.pincode = B.pincode
    where B.pincode is not null
""", df_indian_data=df_indian_data, df_pincode_master=df_pincode_master)
windowSpec = Window.partitionBy("id").orderBy(col("timestamp").desc())
df_merged = df_merged.withColumn("rnk", row_number().over(windowSpec)).filter("rnk=1").drop("rnk")

iceberg_table = "iceberg.airflow_dbt.iceberg_table_fake_indian_data"

if spark_configs.get("incremental", 'N') == "Y":
    mode = "overwrite"
    df_final = df_merged
else:
    mode = "append"
    df_iceberg = spark.table("iceberg.airflow_dbt.iceberg_table_fake_indian_data")
    # df_iceberg = spark.read.format("iceberg").load(iceberg_table)
    # df1 = spark.read.table("iceberg.airflow_dbt.iceberg_table_fake_indian_data") or you can use this as well
    df_final = spark.sql("""
        with distinct_iceberg_file_name as (
            select distinct hdfs_file_name from {df_iceberg}
        ),
        distinct_exploded_file_name as (
            select distinct hdfs_file_name from {df_merged}
        ),
        final_blck as (    
            select distinct A.hdfs_file_name 
            from distinct_exploded_file_name A
            left join distinct_iceberg_file_name B
            on A.hdfs_file_name = B.hdfs_file_name 
            where B.hdfs_file_name is null
        )
        select A.* 
        from {df_merged} A
        join final_blck B 
        on A.hdfs_file_name = B.hdfs_file_name
    """, df_iceberg=df_iceberg, df_merged=df_merged)

df_final = df_final.repartition(10, col("id"))

if df_final.take(1) != [] and mode == "overwrite":
    df_final.write \
    .format("iceberg") \
    .mode(mode) \
    .save(iceberg_table)
else:
    staging_table = "iceberg.airflow_dbt.updates_staging"
    df_final.write.format("iceberg").mode("overwrite").saveAsTable(staging_table)
    update_set = ", ".join([f"t.{c} = u.{c}" for c in df_final.columns if c != "id"])
    insert_cols = ", ".join(df_final.columns)
    insert_vals = ", ".join([f"u.{c}" for c in df_final.columns])
    spark.sql(f"""
        MERGE INTO {iceberg_table} AS t
        USING {staging_table} AS u
        ON t.id = u.id
        WHEN MATCHED THEN UPDATE SET {update_set}
        WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals})
    """)

# df_pincode_master.rdd.getNumPartitions()
# df.rdd.getNumPartitions()
# spark.conf.get("spark.sql.adaptive.enabled")
# spark.conf.get("spark.sql.autoBroadcastJoinThreshold")
# spark.sql("""
#     select pincode, district, statename
#     from {df_pincode_master}
#     group by pincode, district, statename
#     having count(1) > 1
#     limit 10
# """, df_pincode_master=df_pincode_master).show(10)

