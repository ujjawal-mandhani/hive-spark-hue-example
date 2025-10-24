## Example - Spark’s Python DataSource V2 API,

from pyspark.sql.datasource import DataSource, DataSourceReader, DataSourceWriter, WriterCommitMessage
from pyspark.sql.types import StructType, StructField, IntegerType, StringType
from pyspark.sql.functions import *
from pyspark.sql import SparkSession
from pyspark import TaskContext
import zipfile
import csv
import os


class ZippedCSVDataSource(DataSource):
    @classmethod
    def name(cls):
        return "zipped_csv"

    def schema(self):
        schema = self.inferSchema()
        return schema

    def reader(self, schema):
        return ZippedCSVReader(self.options)

    def writer(self, schema, mode):
        return ZippedCSVWriter(self.options, schema)
    
    def inferSchema(self):
        path = self.options["path"]
        first_path = path + os.listdir(path)[0]
        with zipfile.ZipFile(first_path, 'r') as zipf:
            file_name = zipf.namelist()[0]
            with zipf.open(file_name) as f:
                reader = csv.reader(line.decode("utf-8") for line in f)
                header = next(reader)
        return StructType([StructField(col, StringType()) for col in header])

    
class ZippedCSVReader(DataSourceReader):
    def __init__(self, options):
        self.path = options.get("path")
    def read(self, partition):
        path = self.path
        arry_path = os.listdir(path)
        for item in arry_path:
            with zipfile.ZipFile(path + item, 'r') as zipf:
                for name in zipf.namelist():
                    with zipf.open(name) as f:
                        reader = csv.reader(line.decode("utf-8") for line in f)
                        next(reader)  # skip header
                        for row in reader:
                            # yield (row[0], int(row[1]))
                            yield tuple(row)


class ZippedCSVWriter(DataSourceWriter):
    def __init__(self, options, schema):
        self.output_dir = options.get("path")
        self.schema = schema

        # Inorder to check incoming Schema Below is Default Output
        # - ColumnName: DataType()
        # for field in schema.fields:
        #     print(f"  - {field.name}: {field.dataType}")

    def write(self, batch_iter):
        partition_id = TaskContext.get().partitionId()
        tmp_csv = f"/tmp/part_{partition_id}.csv"
        zip_path = os.path.join(self.output_dir, f"part-{partition_id}.zip")
        
        os.makedirs(self.output_dir, exist_ok=True)

        with open(tmp_csv, "w", newline='') as f:
            writer = csv.writer(f)
            writer.writerow([f.name for f in self.schema.fields])
            for row in batch_iter:
                writer.writerow(row)

        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(tmp_csv, arcname="data.csv")

        os.remove(tmp_csv)
        return WriterCommitMessage()


spark = SparkSession.builder.getOrCreate()   
spark.dataSource.register(ZippedCSVDataSource)
df = spark.read.option("header", "true").option("inferSchema", "true").csv("/home/spark-jobs/organisation_data.csv")
df.printSchema()
df.repartition(2).write.format("zipped_csv").option("path", "/home/spark-jobs/write_data").mode("overwrite").save() 

# Read Custom Source Path
df = spark.read.format("zipped_csv").load("/home/spark-jobs/write_data/")
df.printSchema()
df.show(truncate=False)