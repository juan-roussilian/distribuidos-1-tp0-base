#!/bin/bash
SERVER_RESPONSE=$(docker run --rm -i --network tp0_testing_net --entrypoint sh busybox -c 'echo "test" | nc server 12345')
if [ "$SERVER_RESPONSE" = "test" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi