from pyspark.sql import SparkSession
from delta import configure_spark_with_delta_pip
import os

def get_spark():
    builder = SparkSession.builder \
        .appName("LakehouseAnalytics") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .config("spark.driver.memory", "2g")
    spark = configure_spark_with_delta_pip(builder).getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    return spark

def load_csv_to_delta(csv_path, table_name):
    spark = get_spark()
    df = spark.read.option("header", "true").option("inferSchema", "true").csv(csv_path)
    delta_path = f"/home/elakiya/prompt2query/data_storage/{table_name}"
    df.write.format("delta").mode("overwrite").save(delta_path)
    df.createOrReplaceTempView(table_name)
    print(f"Table '{table_name}' loaded successfully.")
    schema = [(f.name, f.dataType.simpleString()) for f in df.schema.fields]
    return schema, delta_path

def get_schema(table_name):
    spark = get_spark()
    delta_path = f"/home/elakiya/prompt2query/data_storage/{table_name}"
    df = spark.read.format("delta").load(delta_path)
    df.createOrReplaceTempView(table_name)
    return [(f.name, f.dataType.simpleString()) for f in df.schema.fields]

def execute_query(sql, table_name):
    spark = get_spark()
    delta_path = f"/home/elakiya/prompt2query/data_storage/{table_name}"
    df = spark.read.format("delta").load(delta_path)
    df.createOrReplaceTempView(table_name)
    result = spark.sql(sql)
    return result.toPandas()