FROM tiangolo/uvicorn-gunicorn-fastapi

RUN apt-get update
RUN apt-get install -y git

# set the working directory in the container
RUN mkdir app/
WORKDIR /app

## Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

## Copy application
COPY app app/
ENV VARIABLE_NAME="application"
