FROM python:2.7
MAINTAINER Gregory Berngardt "gregoryvit@gmail.com"
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt