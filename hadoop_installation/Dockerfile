FROM ubuntu:latest
RUN apt update && apt install -y openssh-server openssh-client hostname telnet tar wget curl openjdk-17-jdk
ENV HADOOP_HOME=/usr/local/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin
# RUN apt-get update && apt-get install -y sudo openssl openssh-client curl bash procps net-tools ssh rsync && rm -rf /var/lib/apt/lists/*
RUN HADOOP_VERSION=$(curl -s https://downloads.apache.org/hadoop/common/ | grep -o 'hadoop-[0-9.]\+/' | sed 's#/##' | sort -V | tail -n 1) && \
    echo "https://downloads.apache.org/hadoop/common/$HADOOP_VERSION/$HADOOP_VERSION-lean.tar.gz" && \
    curl -fL "https://downloads.apache.org/hadoop/common/$HADOOP_VERSION/$HADOOP_VERSION-lean.tar.gz" | tar xfz - -C /usr/local/share && \
    mv "/usr/local/share/$HADOOP_VERSION" "$HADOOP_HOME"
ENV PATH="$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin"
# Basic pseudo-distributed configs (YARN + HDFS in one container)
COPY ./hadoop_config/core-site.xml $HADOOP_CONF_DIR/core-site.xml
COPY ./hadoop_config/hdfs-site.xml $HADOOP_CONF_DIR/hdfs-site.xml
COPY ./hadoop_config/yarn-site.xml $HADOOP_CONF_DIR/yarn-site.xml
COPY ./hadoop_config/mapred-site.xml $HADOOP_CONF_DIR/mapred-site.xml
COPY ./hadoop_config/hadoop-env.sh $HADOOP_CONF_DIR/hadoop-env.sh
COPY ./hadoop_config/workers $HADOOP_CONF_DIR/workers
COPY ./hadoop_config/capacity-scheduler.xml $HADOOP_CONF_DIR/capacity-scheduler.xml
RUN ssh-keygen -A
COPY ./hadoop_config/ssh/sshd_config /etc/ssh/sshd_config
COPY ./hadoop_config/ssh/ssh_config /etc/ssh/ssh_config
RUN mkdir -p /run/sshd
ENV SPARK_HOME=/usr/local/share/spark
RUN SPARK_VERSION=$(curl -s https://downloads.apache.org/spark/ | grep -o 'spark-[0-9.]\+/' | sed 's#/##' | sort -V | tail -n 1) && \
    echo "https://archive.apache.org/dist/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz" && \
    curl -fL "https://archive.apache.org/dist/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz" | tar xfz - -C /usr/local/share && \
    mv "/usr/local/share/$SPARK_VERSION-bin-hadoop3" "$SPARK_HOME"
# COPY spark-3.5.0-bin-hadoop3.tgz .
# RUN tar -xvzf spark-3.5.0-bin-hadoop3.tgz -C /usr/local/share/ && mv /usr/local/share/spark-3.5.0-bin-hadoop3 /usr/local/share/spark && rm spark-3.5.0-bin-hadoop3.tgz
ENV PATH="$PATH:$SPARK_HOME/bin"
ENV PYTHONPATH="$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.9-src.zip"
ENV PYSPARK_PYTHON=/usr/bin/python3
# RUN yum groupinstall "Development Tools" -y && yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make -y  
# \
# && yum install python3.11 python3.11-pip -y && pip3 install pandas pyarrow
RUN curl https://repo1.maven.org/maven2/org/apache/hudi/hudi-spark4.0-bundle_2.13/1.1.0/hudi-spark4.0-bundle_2.13-1.1.0.jar  --output "$SPARK_HOME"/jars/hudi-spark4.0-bundle_2.13-1.1.0.jar && \
curl https://repo1.maven.org/maven2/org/apache/hive/hive-storage-api/2.8.1/hive-storage-api-2.8.1.jar --output "$SPARK_HOME"/jars/hive-storage-api-2.8.1.jar && \
curl https://repo1.maven.org/maven2/org/slf4j/slf4j-api/1.7.36/slf4j-api-1.7.36.jar --output "$SPARK_HOME"/jars/slf4j-api-1.7.36.jar && \
curl https://repo1.maven.org/maven2/org/postgresql/postgresql/42.6.0/postgresql-42.6.0.jar --output "$SPARK_HOME"/jars/postgresql-42.6.0.jar && \
curl https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-4.0_2.13/1.10.0/iceberg-spark-runtime-4.0_2.13-1.10.0.jar --output "$SPARK_HOME"/jars/iceberg-spark-runtime-4.0_2.13-1.10.0.jar
# RUN apt-get update && apt-get install -y python3 python3-pip
# Format HDFS on first start & launch all daemons
COPY entrypoint.sh /entrypoint.sh
COPY ./hadoop_config/ssh/id_rsa /root/.ssh/id_rsa
COPY ./hadoop_config/ssh/id_rsa.pub /root/.ssh/id_rsa.pub
COPY ./hadoop_config/ssh/id_rsa.pub /root/.ssh/authorized_keys
RUN chmod 700 /root/.ssh
RUN chmod 600 /root/.ssh/id_rsa
RUN chmod 644 /root/.ssh/id_rsa.pub /root/.ssh/authorized_keys
RUN chmod +x /entrypoint.sh
# RUN apt-get update && apt-get install -y openjdk-11-jdk
EXPOSE 9870 8088 8042 8020 9000
# RUN yum install -y sudo
# CMD ["sh", "-c", "/usr/sbin/sshd && /entrypoint.sh"]
ENTRYPOINT ["/entrypoint.sh"]
# CMD ["tail", "-f", "/dev/null"]
