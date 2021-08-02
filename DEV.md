# Run local server

uvicorn app.main:application --reload --host 0.0.0.0 --port 8686
gunicorn -b 0.0.0.0:8001 -k uvicorn.workers.UvicornWorker app.main:application


uvicorn app.main:application --reload --host 0.0.0.0 --port 8001 --ssl-keyfile ssl/key.pem --ssl-certfile ssl/cert.pem  --ssl-keyfile-password 12345
gunicorn -b 0.0.0.0:433 --keyfile ssl/key.pem --certfile ssl/cert.pem -k uvicorn.workers.UvicornWorker app.main:application

# run local kibana

docker run --name kibana --net elastic -p 5601:5601 -e "ELASTICSEARCH_HOSTS=http://localhost:9200" docker.elastic.co/kibana/kibana:7.13.3