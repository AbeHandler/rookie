FROM ubuntu:14.04
RUN echo "deb http://archive.ubuntu.com/ubuntu/ $(lsb_release -sc) main univer$
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
RUN pip install flask && pip install boto
RUN mkdir /home/app && cd /home/app && git clone https://github.com/AbeHandler/rookie.git
RUN cd /home/app/rookie &&  pip install -r requirements.txt
RUN pip install cherrypy
RUN export PYTHONPATH=.