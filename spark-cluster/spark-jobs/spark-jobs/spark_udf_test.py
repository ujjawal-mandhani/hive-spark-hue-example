from pyspark.sql import SparkSession
from pyspark import SparkContext, HiveContext
from pyspark.sql import Row
from pyspark.sql.functions import *
import socket


spark = SparkSession.builder \
    .getOrCreate()
    
spark.sparkContext.setLogLevel("DEBUG")

# spark-submit   --master spark://spark-master:7077   --deploy-mode client   --executor-memory 1G  --executor-cores 1 --num-executors 2 spark_udf_test.py
# sc = spark.sparkContext
# acc = sc.accumulator(0)

class foo_bar:
    a = 1
    @classmethod
    def update_value_a(cls):
        cls.a = cls.a + 1
        return str(cls.a) + "_" + str(socket.gethostbyname(socket.gethostname()))

# class foo_bar:
#     def update_value_a(self):
#         acc.add(1)
#         return str(acc.value) + "_" + str(socket.gethostbyname(socket.gethostname()))


spark.udf.register("spark_udf_func_a", foo_bar().update_value_a)


df = spark.range(2, 1002).repartition(5).toDF("id")
df_with_executor = df.withColumn("udf_column", expr("spark_udf_func_a()") ).selectExpr("split(udf_column, '_')[0] as a", "split(udf_column, '_')[1] as ip" )
df_with_executor.persist()
df_with_executor.select("ip").distinct().show(10, truncate=False)
df_with_executor.coalesce(1).write.option("header", "true").mode("overwrite").csv("hdfs://namenode:8020/user/udf/test")

