# Preparing migration scripts for upgrade purpose 


Run 

````
docker-compose -f docker-compose.upgrade.conf up
````

To install two versions of tracardi. Old version is at port 18787 new at 8787.
It will expose redis an elastic on localhost. Make sure you do not have other instances running on these ports. 

Run tracardi-migration-script-builder.

