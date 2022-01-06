![header.jpg](https://raw.githubusercontent.com/atompie/tracardi-images/master/images/github-splash.png)

# Tracardi Open-source Customer Data Platform

[Tracardi](http://www.twitter.com/tracardi) is an open-source Customer Data Platform.

TRACARDI is an API-first solution, low-code / no-code platform aimed at any e-commerce business that 
wants to start using user data for marketing purposes. If you own a brand new e-commerce platform or 
a legacy system you can integrate TRACARDI easily. Use TRACARDI for:

 * **Customer Data Integration** - You can ingest, aggregate and store customer data
   from multiple sources in real time at any scale and speed due to elastic search backend.
   
 * **Customer Data Modelling** -  You can manage data. Define rules that will model data delivered
   from your page and copy it into user profile. You can segment customers into custom segments.
   
 * **User Experience Personalization** - You can personalize user experience with
   real-time customer segmentation and targeting.
   
 * **Profile Unification** - You can merge customer data from various sources to
   single profile. Auto de-duplicate customer records. Blend customers in one account.
   
 * **Automation** - TRACARDI is a great framework for creating
   marketing automation apps. You can send your data to other systems easily

## Screenshots

![flow-1](https://user-images.githubusercontent.com/16271564/145562599-a188de6e-639b-479a-b263-863e9133df53.png)


# Installation

The easiest way to run Tracardi is to run it as a docker container. If you are looking for other installation types visit: [http://docs.tracardi.com/installation/](http://docs.tracardi.com/installation/)

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
docker run -p 8686:80 -e ELASTIC_HOST=http://<your-laptop-ip>:9200 -e USER_NAME=admin -e PASSWORD=admin tracardi/tracardi-api
```

Tracardi must connect to elastic. To do that you have to set ELASTIC_HOST variable to reference your laptop's IP. 

> "Waiting for application startup" issue
> 
> Notice that when type `http://localhost:9200` as ELASTIC_HOST you try to connect to Elastic on localhost. This means that you're
> connecting to the docker itself as localhost means local in docker. Obviously elastic is not there, so Tracardi will
> never connect that is why you see "Waiting for application startup" information. Pass external ip for elastic. This may be your laptop IP if you are running Tracardi locally, e.g. 192.168.1.143:9200. Please refer to Tracardi documentation for more Troubleshooting information.

For more trouble shooting solutions go to [http://docs.tracardi.com/trouble/](http://docs.tracardi.com/trouble/)


## Start Tracardi GUI

Now pull and run Tracardi Graphical User Interface.

```
docker run -p 8787:80 -e API_URL=//127.0.0.1:8686 tracardi/tracardi-gui
```

## Start Tracardi Documentation

Now pull and run Tracardi Documentation.

```
docker run -p 8585:8585 tracardi/tracardi-docs
```

## Log-in

Visit http://127.0.0.1:8787 and login to Tracardi GUI with default username: admin and password: admin. 

## System Documentation

Visit http://127.0.0.1:8585. System documentationis also available at: [http://docs.tracardi.com](http://docs.tracardi.com)

## API Documentation

Visit http://127.0.0.1:8686/docs


# Scaling Tracardi for heavy load. 
 
TRACARDI was developed with scalability in mind. Scaling is as easy as scaling a docker container. 
No additional configuration is needed. 

# Development tracking

TRACARDI is #buildinpublic that means that you can track and influence its development. 

Take a look at [YouTube channel](https://bit.ly/3pbdbPR) and see what Tracardi can do for you.

# Call for contributors

We are looking for contributors. Would you like to help with Tracardi development fork Tracardi or contact us at 
tracardi.cdp@gmail.com or any social platform.

# Support us

If you would like to support us please follow us on [Facebook](https://bit.ly/3uPwP5a) or [Twitter](https://bit.ly/3uVJwLJ), tag us and leave your comments. Subscribe to our [Youtube channel](https://bit.ly/3pbdbPR) to see development process and new upcoming features.

Spread the news about TRACARDI so anyone interested get to know TRACARDI.

We appreciate any help that helps make TRACARDI popular. 

# Donate

You can support us on [BOUNTY-SOURCE](https://www.bountysource.com/teams/tracardi)

# License

Tracardi is available under MIT with Common Clause license.

