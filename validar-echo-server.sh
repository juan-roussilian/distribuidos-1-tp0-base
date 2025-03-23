#!/bin/bash

docker compose -f docker-compose-dev.yaml up -d server-checker
SERVER_RESPONSE=$(docker exec server-checker sh -c "echo -n 'test' | nc -w 1 server 12345")
docker compose -f docker-compose-dev.yaml stop server-checker
if [ "$SERVER_RESPONSE" = "test" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi