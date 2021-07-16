FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

RUN apt-get update
RUN apt-get install -y git

# set the working directory in the container
RUN mkdir app/
WORKDIR /app

## Copy application
COPY app app/
## Install dependencies
RUN pip install -r app/requirements.txt

## Copy manual
COPY manual manual/
## Install dependencies
RUN pip install -r manual/requirements.txt
WORKDIR /app/manual/en
RUN mkdocs build

ENV VARIABLE_NAME="application"
