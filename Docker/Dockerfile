FROM ubuntu:14.04
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main universe" >> /etc/apt/sources.list
RUN apt-get update
RUN apt-get install -y tar \
                   git \
                   curl \
                   nano \
                   wget \
                   dialog \
                   net-tools \
                   build-essential
RUN apt-get install -y python python-dev python-distribute python-pip
RUN pip install flask
RUN mkdir /home/app && cd /home/app && git clone https://github.com/AbeHandler/rookie.git && wget https://gist.githubusercontent.com/AbeHandler/aefa90ac9d5b6d10cc41/raw/ea29c141ae70ccd6ebb76009d2bff18c230d32da/server.py
RUN pip install cherrypy
RUN export PYTHONPATH=.