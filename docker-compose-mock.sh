#!/usr/bin/env bash
set -e

echo "Starting CurrencyMock gRPC container..."

if [ "$(docker ps -aq -f name=currencymock.niffler.dc)" ]; then
  echo "Removing old container currencymock.niffler.dc..."
  docker rm -f currencymock.niffler.dc || true
fi

docker run -d \
  --name currencymock.niffler.dc \
  -p 8888:8888 \
  -p 8094:8094 \
  -v "$(pwd)/wiremock/grpc:/wiremock" \
  -v "$(pwd)/tests/grpc/protos:/proto" \
  -e GRPC_SERVER_PORT=8094 \
  adven27/grpc-wiremock:latest

echo "CurrencyMock container is up and running"
