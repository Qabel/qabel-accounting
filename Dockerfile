FROM alpine:3.5
MAINTAINER Niklas Rust <rust@qabel.de>

RUN apk add --no-cache uwsgi py-pip alpine-sdk bash postgresql-dev uwsgi-python3 
RUN apk add --no-cache --repository http://nl.alpinelinux.org/alpine/3.4/main python3-dev
RUN pip3 install virtualenv requests 
ADD . /app
WORKDIR /app
COPY Docker/invoke.yml qabel.yaml
RUN sh Docker/bootstrap.sh
ENTRYPOINT ["bash", "Docker/startup.sh"]
EXPOSE 5000
