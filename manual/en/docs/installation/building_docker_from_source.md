## Building Tracardi docker from source

Sometimes you will need to build a docker container yourself. 
It is usually needed when you would like your  docker server to run https requests. 

To build a docker container from source clone our repository

```
git clone https://github.com/atompie/tracardi.git
```

Go to tracardi folder and run docker build

```
cd tracardi/
docker build . -t tracardi
```

After a while the docker will be build. It is on your computer, so you can run it like this.

```
docker run -p 8686:80 -e ELASTIC_HOST=http://<your-laptop-ip>:9200 tracardi
```

## SSL Configuration

If you would like to connect Tracardi to HTTPS web page you will need to prepare a docker that can serve HTTPS
request. To do that clone our repository.

```
git clone https://github.com/atompie/tracardi.git
```

Next go to tracardi folder and find file **Dockerfile.ssl** and type path to your SSL certificate and key file. 

* Replace `ssl/key.pem` with a path to your key file
* Replace `ssl/cert.pem` with a path to your certificate

This is how the **Dockerfile.ssl** looks like

```
FROM tiangolo/uvicorn-gunicorn-fastapi

RUN apt-get update
RUN apt-get install -y git

# set the working directory in the container
RUN mkdir app/
WORKDIR /app

## Install dependencies
COPY app/requirements.txt .
RUN pip install -r requirements.txt

## Copy application
COPY app app/
COPY ssl ssl/
COPY manual manual/
ENV VARIABLE_NAME="application"

EXPOSE 433
CMD ["gunicorn", "-b", "0.0.0.0:433", "--keyfile", "ssl/key.pem", "--certfile", "ssl/cert.pem", "-k", "uvicorn.workers.UvicornWorker", "app.main:application"]
```

Then run `docker build`

```
cd tracardi/
docker build . -f Dockerfile.ssl -t tracardi-ssl
```

Once build you can run Tracardi with the following command:

```
docker run -p 8686:80 -e ELASTIC_HOST=http://<your-laptop-ip>:9200 tracardi-ssl
```
