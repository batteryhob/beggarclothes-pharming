FROM ubuntu:18.04

RUN apt-get update && apt-get install -y \
	wget \
	xvfb \
	unzip \
	python3-pip \
	python3-dev \
	python3-setuptools

RUN mkdir -p /app

WORKDIR /app

COPY . /app

RUN pip3 install configparser

ENV LC_ALL=C.UTF-8
ENV PYTHONUNBUFFERED 0

EXPOSE 4000

ENTRYPOINT ["python3", "/app/pharming.py"]