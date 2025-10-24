from pyspark.sql import SparkSession
from pyspark import SparkContext, HiveContext
from pyspark.sql import Row
from pyspark.sql.functions import *

spark = SparkSession.builder \
    .config("hive.metastore.uris", "thrift://metastore:9083") \
    .enableHiveSupport() \
    .getOrCreate()


df = spark.read.option("header", "true").csv("/home/spark-jobs/organisation_data.csv")

df.createOrReplaceTempView("table_temp")
# spark.sql("""
#   select * from default.student2
# """).show()
print("::::::::::::Printing Count", df.count())
spark.sql("drop table if exists temp_table2");
spark.sql("""
  create table temp_table2 as
  select * from table_temp
""")

spark.sql("SHOW TABLES").show()