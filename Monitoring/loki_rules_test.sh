#!/bin/bash

# Đường dẫn tới file docker-compose (nếu cần)
COMPOSE_FILE="../infrastructure/docker-compose.yml"
SERVICE_NAME="loki"

echo "Restart lần 1..."
docker-compose -f $COMPOSE_FILE restart $SERVICE_NAME
sleep 10

echo "Restart lần 2..."
docker-compose -f $COMPOSE_FILE restart $SERVICE_NAME
sleep 10

echo "Restart lần 3..."
docker-compose -f $COMPOSE_FILE restart $SERVICE_NAME

echo "Đã restart $SERVICE_NAME 3 lần trong vòng 1 phút. Hãy kiểm tra alert trên Prometheus/Grafana."
