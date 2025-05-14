#Damit wir standardmäßig python3.10 installieren, welches für evogfuzz benötigt wird
FROM ubuntu:22.04

RUN apt-get update
RUN apt-get -y install git
RUN apt-get -y install python3
RUN apt-get -y install python3-pip
RUN apt-get -y install python3.10-venv

WORKDIR /root/Desktop

RUN mkdir ./scripts
RUN mkdir ./input
RUN mkdir ./output