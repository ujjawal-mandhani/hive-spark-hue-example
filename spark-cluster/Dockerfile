FROM ubuntu:latest
RUN apt update && apt install -y openssh-server openssh-client hostname telnet tar wget curl openjdk-17-jdk netcat-traditional
ENV SPARK_HOME=/usr/local/share/spark
RUN SPARK_VERSION=spark-3.5.0 && \
    echo "https://archive.apache.org/dist/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz" && \
    curl -fL "https://archive.apache.org/dist/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz" | tar xfz - -C /usr/local/share && \
    mv "/usr/local/share/$SPARK_VERSION-bin-hadoop3" "$SPARK_HOME"
ENV PATH="$PATH:$SPARK_HOME/bin"
ENV PYTHONPATH="$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.9-src.zip"
ENV PYSPARK_PYTHON=/usr/bin/python3
# RUN yum groupinstall "Development Tools" -y && yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel  make -y  
# \
# && yum install python3.11 python3.11-pip -y && pip3 install pandas pyarrow
RUN ssh-keygen -A
COPY sshd_config /etc/ssh/sshd_config
COPY ssh_config /etc/ssh/ssh_config
COPY spark-env.sh /usr/local/share/spark/conf/spark-env.sh
COPY slaves /usr/local/share/spark/conf/slaves
ENV HADOOP_HOME=/usr/local/hadoop
RUN HADOOP_VERSION=$(curl -s https://downloads.apache.org/hadoop/common/ | grep -o 'hadoop-[0-9.]\+/' | sed 's#/##' | sort -V | tail -n 1) && \
    echo "https://downloads.apache.org/hadoop/common/$HADOOP_VERSION/$HADOOP_VERSION-lean.tar.gz" && \
    curl -fL "https://downloads.apache.org/hadoop/common/$HADOOP_VERSION/$HADOOP_VERSION-lean.tar.gz" | tar xfz - -C /usr/local/share && \
    mv "/usr/local/share/$HADOOP_VERSION" "$HADOOP_HOME"
ENV PATH="$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin"
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
COPY hadoop_config/core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY hadoop_config/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY hadoop_config/yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml
COPY hadoop_config/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
COPY hadoop_config/hive-site.xml $HADOOP_CONF_DIR/hive-site.xml
COPY hadoop_config/hadoop-env.sh $HADOOP_CONF_DIR/hadoop-env.sh
# RUN yum install -y sudo nc
RUN curl https://repo1.maven.org/maven2/org/apache/hudi/hudi-spark3.5-bundle_2.12/1.0.2/hudi-spark3.5-bundle_2.12-1.0.2.jar --output "$SPARK_HOME"/jars/hudi-spark3.5-bundle_2.12-1.0.2.jar && \
curl https://repo1.maven.org/maven2/org/apache/hive/hive-storage-api/2.8.1/hive-storage-api-2.8.1.jar --output "$SPARK_HOME"/jars/hive-storage-api-2.8.1.jar && \
curl https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar --output "$SPARK_HOME"/jars/slf4j-api-1.7.36.jar && \
curl https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar --output "$SPARK_HOME"/jars/postgresql-42.6.0.jar && \
curl https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.5_2.12/1.9.2/iceberg-spark-runtime-3.5_2.12-1.9.2.jar --output "$SPARK_HOME"/jars/iceberg-spark-runtime-3.5_2.12-1.9.2.jar
# RUN rm -f /etc/yum.repos.d/bintray-rpm.repo && \
#     curl -L https://www.scala-sbt.org/sbt-rpm.repo > sbt-rpm.repo && \
#     mv sbt-rpm.repo /etc/yum.repos.d/ && \
#     yum install sbt -y

# ENV LIVY_HOME=/usr/local/share/livy
# RUN LIVY_VERSION=$(curl -s https://downloads.apache.org/incubator/livy/| grep -o '[0-9.]\+-incubating/' | sed 's#/##' | sort -V | tail -n 1) && \
#     echo https://downloads.apache.org/incubator/livy/${LIVY_VERSION}/apache-livy-${LIVY_VERSION}_2.12-bin.zip && \
#     curl -fL https://downloads.apache.org/incubator/livy/${LIVY_VERSION}/apache-livy-${LIVY_VERSION}_2.12-bin.zip --output ${LIVY_VERSION}.zip && \
#     unzip "$LIVY_VERSION.zip" -d /usr/local/share && \
#     mv /usr/local/share/apache-livy-${LIVY_VERSION}_2.12-bin "$LIVY_HOME" && mkdir -p /usr/local/share/livy/logs && chmod -R 777 /usr/local/share/livy/logs && \
#     rm "$LIVY_VERSION.zip"
# ENV PATH="$PATH:$LIVY_HOME/bin/"
# COPY ./livy_conf/livy.conf "$LIVY_HOME/conf/livy.conf"
# COPY ./livy_conf/livy.jks "$LIVY_HOME/conf/livy.jks"
# COPY ./hadoop_config/workers $HADOOP_CONF_DIR/workers
# RUN yum install python3-pip
# CMD [ "sh", "-c", "/usr/sbin/sshd; sh /usr/local/share/spark/sbin/start-all.sh; yarn --daemon start nodemanager; tail -f /dev/null" ]