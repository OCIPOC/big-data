FROM python:3.9.7

LABEL author="Duy Nguyen"

WORKDIR /work

# Install OpenJDK-11
RUN apt update && \
    apt-get install -y openjdk-11-jdk && \
    apt-get install -y ant && \
    apt-get clean;

# Set JAVA_HOME
ENV JAVA_HOME /usr/lib/jvm/java-11-openjdk-amd64/
RUN export JAVA_HOME

COPY ./requirements.txt ./requirements.txt 

RUN pip install jupyterlab==3.2.9

RUN pip install -r requirements.txt

EXPOSE 8888

# ENTRYPOINT ["jupyter-lab", "--ip 0.0.0.0", "--allow-root"]