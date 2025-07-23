# https://spark.apache.org/docs/latest/api/python/tutorial/sql/python_udtf.html
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.getOrCreate()
spark.sparkContext.setLogLevel("Error")
# Note eval function is mandatory in implementing udtf


@udtf(returnType="protocol: STRING, url: STRING")
class split_with_url_class:
    def eval(self, input_string: str):
        if input_string is None or len(input_string) == 0:
            input_string= '://'
        yield (input_string.split("://")[0], input_string.split("://")[1])
        
@udtf(returnType="Website: STRING, protocol: STRING, url: STRING")
class split_with_url_using_row_class:
    def eval(self, row: Row):
        input_string = row["Website"]
        if input_string is None or len(input_string) == 0:
            input_string= '://'
        yield (input_string, input_string.split("://")[0], input_string.split("://")[1])

spark.udtf.register("split_with_url_protocol", split_with_url_class)
spark.udtf.register("split_with_url_protocol_row", split_with_url_using_row_class)

df = spark.read.option("header", "true").csv("hdfs:///user/spark/scripts/data/organisation_data.csv")
df_final = spark.sql("""
        select Website, protocol, url
        from {df}, LATERAL split_with_url_protocol(Website)
    """, df=df).limit(10)
df_final.show(truncate=False)


df_final = spark.sql("""
        select Website, protocol, url
        from split_with_url_protocol_row(TABLE({df}))
    """, df=df).limit(10)

df_final.show(truncate=False)

spark.stop()