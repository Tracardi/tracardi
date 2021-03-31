# Docker build
docker build . -t tracardi-free



uvicorn app.main:application --reload --host 0.0.0.0


