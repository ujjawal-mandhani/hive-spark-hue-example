docker tag hive-example_spark-master localhost:10004/hive-hue-spark/hive-example_spark-master
docker tag gethue/hue localhost:10004/hive-hue-spark/gethue/hue
docker tag postgres localhost:10004/hive-hue-spark/postgres
docker tag apache/hive:4.0.0 localhost:10004/hive-hue-spark/apache/hive:4.0.0
docker tag hive-example_spark-worker-2 localhost:10004/hive-hue-spark/hive-example_spark-worker-2
docker tag hive-example_spark-worker-1 localhost:10004/hive-hue-spark/hive-example_spark-worker-1


docker push localhost:10004/hive-hue-spark/hive-example_spark-master
docker push localhost:10004/hive-hue-spark/gethue/hue
docker push localhost:10004/hive-hue-spark/postgres
docker push localhost:10004/hive-hue-spark/apache/hive:4.0.0
docker push localhost:10004/hive-hue-spark/hive-example_spark-worker-2
docker push localhost:10004/hive-hue-spark/hive-example_spark-worker-1


docker rmi localhost:10004/hive-hue-spark/hive-example_spark-master
docker rmi localhost:10004/hive-hue-spark/gethue/hue
docker rmi localhost:10004/hive-hue-spark/postgres
docker rmi localhost:10004/hive-hue-spark/apache/hive:4.0.0
docker rmi localhost:10004/hive-hue-spark/hive-example_spark-worker-2
docker rmi localhost:10004/hive-hue-spark/hive-example_spark-worker-1


docker rmi hive-example_spark-master
docker rmi gethue/hue
docker rmi postgres
docker rmi apache/hive:4.0.0
docker rmi hive-example_spark-worker-2
docker rmi hive-example_spark-worker-1


docker pull localhost:10004/hive-hue-spark/hive-example_spark-master
docker pull localhost:10004/hive-hue-spark/gethue/hue
docker pull localhost:10004/hive-hue-spark/postgres
docker pull localhost:10004/hive-hue-spark/apache/hive:4.0.0
docker pull localhost:10004/hive-hue-spark/hive-example_spark-worker-2
docker pull localhost:10004/hive-hue-spark/hive-example_spark-worker-1


docker tag localhost:10004/hive-hue-spark/hive-example_spark-master hive-example_spark-master
docker tag localhost:10004/hive-hue-spark/gethue/hue gethue/hue
docker tag localhost:10004/hive-hue-spark/postgres postgres
docker tag localhost:10004/hive-hue-spark/apache/hive:4.0.0 apache/hive:4.0.0
docker tag localhost:10004/hive-hue-spark/hive-example_spark-worker-2 hive-example_spark-worker-2
docker tag localhost:10004/hive-hue-spark/hive-example_spark-worker-1 hive-example_spark-worker-1