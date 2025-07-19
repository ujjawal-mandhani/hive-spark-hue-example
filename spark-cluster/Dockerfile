FROM openjdk:latest
RUN microdnf update
RUN microdnf install yum
ENV SPARK_HOME=/usr/local/share/spark
RUN SPARK_VERSION=$(curl -s https://downloads.apache.org/spark/ | grep -o 'spark-[0-9.]\+/' | sed 's#/##' | sort -V | tail -n 1) && \
    echo "https://downloads.apache.org/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz" && \
    curl -fL "https://downloads.apache.org/spark/$SPARK_VERSION/$SPARK_VERSION-bin-hadoop3.tgz" | tar xfz - -C /usr/local/share && \
    mv "/usr/local/share/$SPARK_VERSION-bin-hadoop3" "$SPARK_HOME"
ENV PATH="$PATH:$SPARK_HOME/bin"
ENV PYTHONPATH="$SPARK_HOME/python:$SPARK_HOME/python/lib/py4j-0.10.9.9-src.zip"
ENV PYSPARK_PYTHON=/usr/bin/python3
RUN yum install -y openssh-server openssh-clients hostname telnet 
RUN yum groupinstall "Development Tools" -y && yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel wget make -y  \
&& yum install python3.11 python3.11-pip -y && pip3 install pandas pyarrow
RUN ssh-keygen -A
COPY sshd_config /etc/ssh/sshd_config
COPY ssh_config /etc/ssh/ssh_config
COPY spark-env.sh /usr/local/share/spark/conf/spark-env.sh
COPY slaves /usr/local/share/spark/conf/slaves
# RUN yum install python3-pip
CMD [ "sh", "-c", "/usr/sbin/sshd && sh /usr/local/share/spark/sbin/start-all.sh && tail -f /dev/null" ]