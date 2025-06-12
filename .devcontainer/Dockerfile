FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    git \
    fonts-dejavu-core \
    && apt-get clean

COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app
