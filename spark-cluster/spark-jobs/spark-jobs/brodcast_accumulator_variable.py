from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

spark = SparkSession.builder.getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
sc = spark.sparkContext
lookup_dict = {"1": 1, "2": 2}
broadcast_lookup = sc.broadcast(lookup_dict)

# In order to reintialize the brodcast variable use below commands
# broadcast_lookup.unpersist()
# broadcast_lookup = sc.broadcast({"A": 1, "B": 2, "C": 3})

def map_broadcast(x):
    return broadcast_lookup.value.get(x, 0)

map_udf = spark.udf.register("map_udf",map_broadcast, IntegerType())

df = spark.read.option("header", "true").csv("./organisation_data.csv")
df_final = spark.sql("""
    select Index, map_udf(Index) as mppr_udf
    from {df}
""", df=df).filter("mppr_udf!= 0").show(truncate=False)


### Accumulator Example 

acc = sc.accumulator(0)
def check_counter(x):
    if x.Index is not None:
        acc.add(1)
    return str(x)
df.limit(10).rdd.foreach(check_counter)
print("::::::Count of Df", acc.value)

spark.stop()