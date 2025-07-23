#!/usr/bin/env bash
# set -e
# set -euo pipefail
# mkdir -p /hadoop_data
/usr/sbin/sshd || echo "WARNING: sshd failed to start; continuing..."

# if [ ! -f /hadoop_data/.formatted ]; then
#   echo "Formatting HDFS..."
#   $HADOOP_HOME/bin/hdfs namenode -format -force
#   touch /hadoop_data/.formatted
# fi

NAMENODE_DIR=/opt/hadoop/data/nameNode
mkdir -p $NAMENODE_DIR

# Format HDFS if not formatted
if [ ! -d "$NAMENODE_DIR/current" ]; then
  echo "Formatting HDFS NameNode at $NAMENODE_DIR..."
  $HADOOP_HOME/bin/hdfs namenode -format -force
fi

echo "Starting HDFS..."
$HADOOP_HOME/sbin/start-dfs.sh
# yarn --daemon start resourcemanager

echo "Starting YARN..."
# $HADOOP_HOME/sbin/start-yarn.sh
echo "Starting NameNode..."
$HADOOP_HOME/bin/hdfs --daemon start namenode

echo "Starting SecondaryNameNode..."
$HADOOP_HOME/bin/hdfs --daemon start secondarynamenode

echo "Starting YARN ResourceManager..."
yarn --daemon start resourcemanager

# Keep container alive by tailing logs
# tail -f $HADOOP_HOME/logs/*.log
tail -f /dev/null
