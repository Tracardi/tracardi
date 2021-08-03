docker build . -t tracardi/tracardi:0.5.0.rc-1
docker push tracardi/tracardi:0.5.0.rc-1

docker build . -t tracardi/tracardi
docker push tracardi/tracardi
