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
RUN apt-get update && apt-get install -y python-software-properties software-properties-common postgresql-9.3 postgresql-client-9.3 postgresql-contrib-9.3
RUN apt-get install -y libpq-dev python-dev
RUN apt-get install -y lib32ncurses5-dev
RUN apt-get install -y libblas-dev liblapack-dev
RUN apt-get install -y gfortran
RUN mkdir /home/app && cd /home/app && git clone https://github.com/AbeHandler/rookie.git
RUN mkdir /home/app/rookie/indexes
RUN mkdir /home/app/rookie/indexes/lens
RUN export PYTHONPATH=.
RUN cd /home/app/rookie &&  pip install -r requirements.txt
RUN cd /home/app/rookie

