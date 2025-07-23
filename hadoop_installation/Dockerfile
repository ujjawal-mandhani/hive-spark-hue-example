# Dockerfile.hadoop-yarn
# FROM openjdk:11-jre-slim
FROM openjdk:11-jdk-slim
ENV HADOOP_HOME=/usr/local/hadoop
ENV HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
ENV JAVA_HOME=/usr/local/openjdk-11
ENV PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin
RUN apt-get update && apt-get install -y sudo openssl openssh-client curl bash procps net-tools ssh rsync && rm -rf /var/lib/apt/lists/*
RUN HADOOP_VERSION=$(curl -s https://downloads.apache.org/hadoop/common/ | grep -o 'hadoop-[0-9.]\+/' | sed 's#/##' | sort -V | tail -n 1) && \
    echo "https://downloads.apache.org/hadoop/common/$HADOOP_VERSION/$HADOOP_VERSION.tar.gz" && \
    curl -fL "https://downloads.apache.org/hadoop/common/$HADOOP_VERSION/$HADOOP_VERSION.tar.gz" | tar xfz - -C /usr/local/share && \
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
RUN apt-get update && apt-get install -y python3 python3-pip
# Format HDFS on first start & launch all daemons
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
# RUN apt-get update && apt-get install -y openjdk-11-jdk
EXPOSE 9870 8088 8042 8020 9000
# CMD ["sh", "-c", "/usr/sbin/sshd && /entrypoint.sh"]
ENTRYPOINT ["/entrypoint.sh"]
# CMD ["tail", "-f", "/dev/null"]
