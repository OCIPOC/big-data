# builder step used to download and configure spark environment
FROM openjdk:11.0.11-jre-slim-buster as builder

LABEL MAINTAINER "Duy Nguyen <duynguyenngoc@hotmail.com>"


# Fix the value of PYTHONHASHSEED
# Note: this is needed when you use Python 3.3 or greater
ENV SPARK_VERSION=3.2.1 \
    HADOOP_VERSION=3.3.2 \
    HADOOP_VERSION_SPARK=3.2 \
    SPARK_HOME=/opt/spark \
    PYTHON_VERSION=3.9.7


# Add Dependencies for PySpark
RUN apt-get update && apt-get install -y curl vim wget software-properties-common \
        net-tools ca-certificates \
        build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
        libnss3-dev libssl-dev libreadline-dev libffi-dev ssh
    
RUN apt-get install -y python3-pip python3-numpy python3-matplotlib python3-scipy python3-pandas python3-simpy


# Add Install Python3.9
# Note: we want to using tensorflow 2.8.0
RUN add-apt-repository ppa:deadsnakes/ppa

RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tar.xz \
    && tar -xf Python-${PYTHON_VERSION}.tar.xz && cd Python-${PYTHON_VERSION} \
    && ./configure --prefix=/usr/local/python3 --enable-optimizations \
    && make && make install \
    && ln -sf /usr/local/python3/bin/python3.9 /usr/bin/python3 \
    && ln -sf /usr/local/python3/bin/pip3 /usr/bin/pip3

COPY ./lsb_release /usr/bin/lsb_release

# Install Requirement python3 pip
COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt


# Download and uncompress spark from the apache archive
RUN wget --no-verbose -O apache-spark.tgz "https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION_SPARK}.tgz" \
    && mkdir -p /opt/spark \
    && tar -xf apache-spark.tgz -C /opt/spark --strip-components=1 \
    && rm apache-spark.tgz


# Apache spark environment
FROM builder as apache-spark

WORKDIR /opt/spark

ENV SPARK_MASTER_PORT=7077 \
SPARK_MASTER_WEBUI_PORT=8080 \
SPARK_LOG_DIR=/opt/spark/logs \
SPARK_MASTER_LOG=/opt/spark/logs/spark-master.out \
SPARK_WORKER_LOG=/opt/spark/logs/spark-worker.out \
SPARK_WORKER_WEBUI_PORT=8080 \
SPARK_WORKER_PORT=7000 \
SPARK_MASTER="spark://spark-master:7077" \
SPARK_WORKLOAD="master"

EXPOSE 8080 7077 6066

RUN mkdir -p $SPARK_LOG_DIR && \
touch $SPARK_MASTER_LOG && \
touch $SPARK_WORKER_LOG && \
ln -sf /dev/stdout $SPARK_MASTER_LOG && \
ln -sf /dev/stdout $SPARK_WORKER_LOG

COPY start-spark.sh /

COPY ./jars/* /opt/spark/jars/

CMD ["/bin/bash", "/start-spark.sh"]