FROM alpine:latest

RUN apk update 
RUN apk add git
RUN apk add python3
RUN apk add py3-pip
RUN apk add gcc python3-dev musl-dev linux-headers

WORKDIR /root/Desktop

RUN mkdir ./scripts