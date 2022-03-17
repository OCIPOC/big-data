FROM duynguyenngoc/hadoop-base:3.3.2

LABEL MAINTAINER "Duy Nguyen <duynguyenngoc@hotmail.com>"

# HDFS
ENV HDFS_CONF_dfs_namenode_name_dir=file:///hadoop/dfs/name
RUN mkdir -p /hadoop/dfs/name
VOLUME /hadoop/dfs/name

# Execution
ADD run.sh /
RUN chmod a+x /run.sh

EXPOSE 9870 9000

CMD ["/run.sh"]

