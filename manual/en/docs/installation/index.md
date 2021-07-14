# Installation

The easiest way to run Tracardi is to run it as a docker container. 

In order to do that you must have docker installed on your local machine. 
Please refer to docker installation manual to see how to install docker.

## Dependencies

Tracardi need elasticsearch as its backend. Please pull and run elasticsearch single node docker before you start Tracardi. 

You can do it with this command.
```
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.13.2
```

## Start Tracardi API

Now pull and run Tracardi backend.

```
docker run -p 8686:80 -e ELASTIC_HOST=http://<your-laptop-ip>:9200 tracardi/tracardi:0.5.0.rc-1
```

Tracardi must connect to elastic. To do that you have to set ELASTIC_HOST variable to reference your laptop's IP. 

## Start Tracardi GUI

Now pull and run Tracardi Graphical User Interface.

```
docker run -p 8787:80 -e API_URL=http://127.0.0.1:8686 tracardi/tracardi-gui:0.5.0.rc-1
```

## Log-in

Visit http://127.0.0.1:8787 and login to Tracardi GUI.

# Running Tracardi with docker compose

```
docker-compose up
```

This will build and install Tracardi and all required dependencies such as elastic search on your computer. 
Hence that this type of setup is for demonstration purpose only.