FROM stackbrew/ubuntu:14.04
MAINTAINER Ben Firshman "ben@orchardup.com"
RUN apt-get update -qq && apt-get -y install nginx
RUN apt-get -y install python-pip
RUN pip install Flask
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
RUN mkdir /etc/nginx/ssl
ADD default /etc/nginx/sites-available/default
ADD default-ssl /etc/nginx/sites-available/default-ssl
RUN mkdir /var/www && echo "test page running on docker" > /var/www/index.html

EXPOSE 80

CMD ["nginx"]