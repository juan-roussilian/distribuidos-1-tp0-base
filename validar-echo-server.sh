    #!/bin/bash

# Para verificar el funcionamiento, levantar cliente con:
# docker compose -f docker-compose-dev.yaml up -d client1
# ya que es el cliente quien se encarga de comprobar el 
# funcionamiento del servidor

SERVER_RESPONSE=$(docker exec -i client1 sh -c 'echo -n "test" | nc -w 5 172.25.125.2 12345')
if [ "$SERVER_RESPONSE" == "test" ]; then
    echo "action: test_echo_server | result: success"
else
    echo "action: test_echo_server | result: fail"
fi