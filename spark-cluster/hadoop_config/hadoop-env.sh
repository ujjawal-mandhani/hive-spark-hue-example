export HADOOP_ROOT_LOGGER="INFO,console"
export HADOOP_OPTS="-Djava.library.path=$HADOOP_HOME/lib/native"

# Prevent use of sudo (Docker runs as root)
export HDFS_NAMENODE_USER=root
export HDFS_DATANODE_USER=root
export HDFS_SECONDARYNAMENODE_USER=root
export YARN_RESOURCEMANAGER_USER=root
export YARN_NODEMANAGER_USER=root
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64