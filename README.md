![github_banner](https://user-images.githubusercontent.com/16271564/148845983-7c9e85c1-465f-44ed-b1e9-7112908d2e83.png)

[![Stargazers repo roster for @tracardi/tracardi](https://reporoster.com/stars/tracardi/tracardi)](https://github.com/tracardi/tracardi/stargazers)

[![contributors](https://opencollective.com/tracardi-cdp/tiers/badge.svg)](https://opencollective.com/tracardi-cdp)
[![Become a backer](https://opencollective.com/tracardi-cdp/tiers/backers.svg?avatarHeight=36)](https://opencollective.com/tracardi-cdp)

# Open-source Customer Engagement and Data Platform

[Tracardi](http://www.tracardi.com) is an open-source system that supports customer engagement and enhances the consumer experience.
Tracardi is intended for anyone who carries out any type of customer interaction, be it through sales or service delivery.
Tracardi collects data from customer journeys and assigns it to a profile that is maintained throughout the period of interaction with the customer.

You can support the project on [Open Collective](https://www.opencollective.com/tracardi-cdp)

## Screenshots

![flow-1](https://user-images.githubusercontent.com/16271564/145562599-a188de6e-639b-479a-b263-863e9133df53.png)

# Introduction

TRACARDI is an API-first solution, low-code / no-code platform aimed at any business that 
wants to start using user data for automated customer engagement. If you own a brand new e-commerce platform or 
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

If you want to see Tracardi in action subscribe to our [Youtube channel](https://bit.ly/3pbdbPR).

# Installation

The easiest way to run Tracardi is to run it as a docker container. If you are looking for other installation types visit: [http://docs.tracardi.com/installation/](http://docs.tracardi.com/installation/)

In order to do that you must have docker installed on your local machine. 
Please refer to docker installation manual to see how to install docker.

## One line installation

Open tracardi project and run:

```
docker-compose up
```

Visit http://127.0.0.1:8787 and complete installation in Tracardi GUI. 

## Run each docker container one-by-one

### Dependencies

Tracardi need elasticsearch and redis as its backend. 

#### Elasticsearch

Please pull and run elasticsearch single node docker before you start Tracardi. 

You can do it with this command.
```
docker run -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" docker.elastic.co/elasticsearch/elasticsearch:7.13.2
```

#### Redis

You will need a redis instance as well. 

Start it with:

```
docker run -p 6379:6379 redis
```

### Run Tracardi API

Now pull and run Tracardi backend.

```
docker run -p 8686:80 -e ELASTIC_HOST=http://<your-laptop-ip>:9200 -e REDIS_HOST=redis://<your-laptop-ip>:6379 tracardi/tracardi-api:0.7.1
```

You can remove `-e REDIS_HOST=redis://<your-laptop-ip>:6379` if you did not start redis. Without redis some system features are 
unavailable. 

Tracardi must connect to elastic. To do that you have to set ELASTIC_HOST variable to reference your laptop's IP. 

> "Waiting for application startup" issue
> 
> Notice that when type `http://localhost:9200` as ELASTIC_HOST you try to connect to Elastic on localhost. This means that you're
> connecting to the docker itself as localhost means local in docker. Obviously elastic is not there, so Tracardi will
> never connect that is why you see "Waiting for application startup" information. Pass external ip for elastic. This may be your laptop IP if you are running Tracardi locally, e.g. 192.168.1.143:9200. Please refer to Tracardi documentation for more Troubleshooting information.

For more trouble shooting solutions go to [http://docs.tracardi.com/trouble/](http://docs.tracardi.com/trouble/)

### Connecting Tracardi to Elastic via SSL connection

If you have an elasticsearch instance and you would like to connect to it via HTTPS this is the command you may find useful. 

```
docker run -p 8686:80 -e ELASTIC_HOST=https://user:password@<your-laptop-ip>:9200 -e ELASTIC_VERIFY_CERTS=no -e REDIS_HOST=redis://<your-laptop-ip>:6379 tracardi/tracardi-api:0.7.1
```

### Open Tracardi GUI

Now pull and run Tracardi Graphical User Interface.

```
docker run -p 8787:80 -e API_URL=//127.0.0.1:8686 tracardi/tracardi-gui:0.7.1
```

## Need help ?


<p align="center">
    Join our community
<br/>
<a href="https://join.slack.com/t/tracardi/shared_invite/zt-10y7w0o9y-PmCBnK9qywchmd1~KIER2Q">
    <img src="https://user-images.githubusercontent.com/16271564/151843970-5e869807-4ccf-46ab-98f5-6a65aea790f8.png" width="120px"/> 
</a>
</p>


## Start Tracardi Documentation

Now pull and run Tracardi Documentation.


```
docker run -p 8585:8585 tracardi/tracardi-docs
```

## Log-in

Visit http://127.0.0.1:8787 and complete installation in Tracardi GUI. 

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

You can support us on [Open Collective](https://www.opencollective.com/tracardi-cdp)


# Referral programs

Support us via referral programs. If you buy service from the following link to support the project.

[![DigitalOcean Referral Badge](https://web-platforms.sfo2.digitaloceanspaces.com/WWW/Badge%203.svg)](https://www.digitalocean.com/?refcode=882eb4bf23be&utm_campaign=Referral_Invite&utm_medium=Referral_Program&utm_source=badge)


# License

Tracardi is available under MIT with Common Clause license.

[![Forkers repo roster for @tracardi/tracardi](https://reporoster.com/forks/tracardi/tracardi)](https://github.com/tracardi/tracardi/network/members)

