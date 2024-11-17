FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

RUN apt update && apt upgrade -y
RUN apt install -y libgl1

RUN pip install --no-cache-dir --upgrade setuptools wheel pip

COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt