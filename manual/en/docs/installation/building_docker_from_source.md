## Building Tracardi docker from source


```
git clone https://github.com/atompie/tracardi.git
cd tracardi/
docker build . -t tracardi
docker run -p 8686:80 -e ELASTIC_HOST=http://<your-laptop-ip>:9200 tracardi
```