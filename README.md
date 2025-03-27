# Ejecución de la solución 
## Ejercicio 1
Para validar el correcto funcionamiento del script ejecutar el siguiente comando sobre la raiz del proyecto

```./generar-compose.sh docker-compose-dev.yaml 5 ```

Luego verificar la salida del script y el contenido del archivo `docker-compose-dev.yaml` para validar su correcta creacion con 5 clientes y ejecutar:

```make docker-compose-up```

Seguido de:  

```make docker-compose-logs```

Para observar a los clientes y al servidor interactuando

## Ejercicio 2

Para validar que los sericios esten tomando correctamente la configuracion de los archivos config sin tener que volver a buildear la imagen podemos setear el valor de `LOGGING_LEVEL` en  `server/config.ini` y `log.level` en `client/config.yaml` ambos en `INFO` y ejecutar los siguientes comandos para ver en los logs que ambos se inicializan con el valor de level en INFO


```console
make docker-compose-up
make docker-compose-logs
```
Para levantar ambos. Luego podemos detener el cliente. Actualizar el valor de log a "DEBUG" y ver que cuando lo levantamos se imprime en el log de config, que el level es "DEBUG" y nose tuvo que buildear la imagen dos veces

```console
docker compose -f docker-compose-dev.yaml stop client1
docker compose up -f docker-compose-dev.yaml stop client1
make docker-compose-logs
```

## Ejercicio 3

Para comprobar que el script de `validar_echo_server.sh` funciona, podemos validar el caso donde el servidor esta funcionando ejectuando

```console
make docker-compose-up
./validar_echo_server.sh`
```

y vamos a ver como se retorna por consola "success" denotando que el servidor respondio correctamente. Para el caso contrario, eliminamos la ejecucion del servidor y corremos nuevamente el validador


```console
docker compose -f docker-compose-dev.yaml stop server
./validar_echo_server.sh`
```

y veremos como la respuesta es "fail"

## Ejercicio 4

Aqui queremos comprobar el correcto funcionamiento de la señal de sigterm que se envia cuando realizamos un docker compose down sobre un servicio. Por lo tanto la mejor forma de probarlo es levantando tanto el cliente como el servidor,  y detenerlos rapidamente. Luego revisando los logs veremos que no hubo errores en la ejecucion de ambos

```console
make docker-compose-up
docker compose  -f docker-compose-dev.yaml stop server
docker compose  -f docker-compose-dev.yaml stop client1
make docker-compose-logs
```

## Ejercicio 5 

Se pueden modificar las variables de entorno que se le envian a los clientes en el archivo docker-compose-dev.yaml multiples veces y por cada modificacion realizar:

```console
make docker-compose-up
make docker-compose-logs
```

Para ver la interacion de los mensajes de apuestas del cliente con el servidor con los nuevos valores definidos

### Protocolo 
Se definieron los siguientes mensajes a enviar por el cliente y el servidor en un protocolo binario mixto, en el cual hay parametros fijos, en su mayoría los valores numéricos, y parametros variables que deben a su vez ir acompañados de un numero representando su longitud en bytes. Finalmente el tamaño de paquete de apuesta debe ser fijo ya que no se implementa un parametro de tamaño total de paquete y ademas no se considera que sea necesario porque los campos dinamicos correspondiente al nombre y apellido de quien realizo la apuesta no deberian utilizar mas de los bytes que tienen disponibles. 


| Tipo de mensaje  | OP-CODE | Tamaño | Composición del mensaje |
|------------------|---------|--------|--------------------------|
| ACK - Éxito     | 0       | 2B     | OPCODE (2B)              |
| Enviar una apuesta | 1       | 150B   | OPCODE (2B), AGENCIA_ID (2B), DOCUMENTO (4B), NUMERO (2B), NACIMIENTO (10B), TAM_NOMBRE (2B), NOMBRE (DINÁMICO), TAM_APELLIDO (2B), APELLIDO (DINÁMICO), PADDING |

La interaccion se realiza de forma que el cliente envia su apuesta y hasta que no recibe su mensaje de exito se queda bloqueado esperando a leer los bytes de opcode de este mensaje

## Ejercicio 6
Se puede modificar la variable de configuracion del cliente max amount y ver como se envian esa cantidad de apuestas del cliente al servidor

```console
make docker-compose-up
make docker-compose-logs
```
### Protocolo
 
Para este ejercicio se reemplaza el mensaje de una unica apuesta por el mensaje de apuestas en lote. Nuevamente, se mantiene el esquema de parametros mixtos, pero ahora se le agrega que el tamaño maximo del paquete no debe superar los 8000 bytes, por lo tanto se hace uso de la variable de configuracion maxAmount para configurar el tamaño maximo de lote. Si este fuera un valor que hiciera que el paquete de lote superara los 8kb, se sea al valor maximo, que dado el tamaño del payload de las apuestas fijo en 144B, maxAmount es 55.

Tambíen se adelanto la creación el mensaje de fin de apuestas del ejercicio 7 a esta parte del protocolo ya que es util para decidir cuando el cliente debe terminar su ejecución.


| Tipo de mensaje        | OP-CODE | Tamaño  | Composición del mensaje |
|------------------------|---------|--------|--------------------------|
| ACK - Éxito           | 0       | 2B     | OPCODE (2B)              |
| Enviar lote apuestas  | 1       | Max 8KB | OPCODE (2B), AGENCIA_ID (2B), CANTIDAD_APUESTAS (2B), APUESTAS (144B x #APUESTAS) |
| Error múltiples apuestas | 2       | 2B     | OPCODE (2B)              |
| Fin apuestas        | 3       | 4B      | OPCODE (2B), AGENCIA_ID (2B) |

## Ejercicio 7

Para validar el correcto funcionamiento de este ejercicio, se pueden modificar los archivos .csv correspondiente a las apuestas de cada cliente y verificar como esto afecta al mensaje final de calculo de ganadores de cada agencia. Como por defecto el ganador siempre sera quien apueste al numero 7574, se pueden agregar o eliminar apuestas con este numero y ver como asciende o desciende la cantidad de ganadores en el ultimo mensaje que recibe cada cliente.

```console
make docker-compose-up
```

y luego de que termina la ejecución de los clientes:

```console
make docker-compose-logs
```

### Protocolo 
Se agregan los mensajes de consulta de ganadores y respuesta por parte del servidor. 
El mensaje de respuesta de ganadores es dinamico ya que no se puede saber de antemano la canitdad de ganadores que puede tener una agencia, sin embargo dado que son numeros representados en 2B se opto por no poner un limite al tamaño del mensaje, ya que en casos extremos sería grande, pero en casos normales no.

|Tipo de mensaje       | OP-CODE | Tamaño   | Composición del mensaje |
|----------------------|---------|---------|--------------------------|
| Consulta ganadores  | 4       | 4B      | OPCODE (2B), AGENCIA_ID (2B) |
| Respuesta ganadores | 5       | Sin limite | OPCODE (2B), CANTIDAD_GANADORES (2B), GANADORES (2B x #GANADORES ) |


## Ejercicio 8

Finalmente para validar el correcto funcionamiento del ejercicio, además de las pruebas manuales del ejercicio 7, se debe prestar atencion al orden de los mensajes en los logs. Al poder procesar de manera concurrente el protocolo de transferencia con cada cliente, con mucha probabilidad se veran  intercalados mensajes de todos los clientes, cuando antes no existia tal intercalado.


```console
make docker-compose-up
```

y luego de que termina la ejecución de los clientes:

```console
make docker-compose-logs
```

### Concurrencia

Se opto por aplicar multiprocessing siguiendo las recomendaciones de la cátedra para evitar los problemas de performance que introduce el GIL en python.

Para ello, se crean un proceso (el proceso principal) para aceptar nuevas conexiones, y un proceso por cada conexion para manejar el protocolo de transferencia de apuestas con el cliente. Estos procesos viven hasta que reciben la consulta del cliente de los ganadores, y es este mensaje el que marca el fin del protocolo. Una vez se "termino" el protocolo para cada cliente, se procesan los ganadores y se crea un nuevo proceso por cada cliente que se encarga de comunicar de manera paralela los ganadores. 

Las secciones criticas donde puedes ocurrir una race condition son:
- Al momento de almacenar apuestas, y es por eso que se implementa un lock multi proceso que se debe adquirir antes de poder persistir la apuesta
- Al momento de sumar un proceso a la lista de procesos terminados, la cual es compartida entre procesos. Para solucionar esto se utilizo una lista de la libreria multiprocessing la cual internamente implementa el mecanismo de sincronización entre procesos. Se opto por esta solución en lugar de utilizar otro lock multiproceso ya que resulta técnicamente mas interesante y agrega variedad a los mecanismos de sincronización empleados.


# Puntos de mejora

Surgió como posible diseño alternativo el uso de una cola bloqueante y un proceso extra el cual se encargase de almacenar las apuestas, pero dado que antes de seguir efectuando el protocolo el servidor debe verificar que la operacion de persistir haya sido realizada sin errores, esta opcion no agregaría mejoras en la performance paralela de los proceso

# Enunciado | TP0: Docker + Comunicaciones + Concurrencia

En el presente repositorio se provee un esqueleto básico de cliente/servidor, en donde todas las dependencias del mismo se encuentran encapsuladas en containers. Los alumnos deberán resolver una guía de ejercicios incrementales, teniendo en cuenta las condiciones de entrega descritas al final de este enunciado.

 El cliente (Golang) y el servidor (Python) fueron desarrollados en diferentes lenguajes simplemente para mostrar cómo dos lenguajes de programación pueden convivir en el mismo proyecto con la ayuda de containers, en este caso utilizando [Docker Compose](https://docs.docker.com/compose/).

## Instrucciones de uso
El repositorio cuenta con un **Makefile** que incluye distintos comandos en forma de targets. Los targets se ejecutan mediante la invocación de:  **make \<target\>**. Los target imprescindibles para iniciar y detener el sistema son **docker-compose-up** y **docker-compose-down**, siendo los restantes targets de utilidad para el proceso de depuración.

Los targets disponibles son:

| target  | accion  |
|---|---|
|  `docker-compose-up`  | Inicializa el ambiente de desarrollo. Construye las imágenes del cliente y el servidor, inicializa los recursos a utilizar (volúmenes, redes, etc) e inicia los propios containers. |
| `docker-compose-down`  | Ejecuta `docker-compose stop` para detener los containers asociados al compose y luego  `docker-compose down` para destruir todos los recursos asociados al proyecto que fueron inicializados. Se recomienda ejecutar este comando al finalizar cada ejecución para evitar que el disco de la máquina host se llene de versiones de desarrollo y recursos sin liberar. |
|  `docker-compose-logs` | Permite ver los logs actuales del proyecto. Acompañar con `grep` para lograr ver mensajes de una aplicación específica dentro del compose. |
| `docker-image`  | Construye las imágenes a ser utilizadas tanto en el servidor como en el cliente. Este target es utilizado por **docker-compose-up**, por lo cual se lo puede utilizar para probar nuevos cambios en las imágenes antes de arrancar el proyecto. |
| `build` | Compila la aplicación cliente para ejecución en el _host_ en lugar de en Docker. De este modo la compilación es mucho más veloz, pero requiere contar con todo el entorno de Golang y Python instalados en la máquina _host_. |

### Servidor

Se trata de un "echo server", en donde los mensajes recibidos por el cliente se responden inmediatamente y sin alterar. 

Se ejecutan en bucle las siguientes etapas:

1. Servidor acepta una nueva conexión.
2. Servidor recibe mensaje del cliente y procede a responder el mismo.
3. Servidor desconecta al cliente.
4. Servidor retorna al paso 1.


### Cliente
 se conecta reiteradas veces al servidor y envía mensajes de la siguiente forma:
 
1. Cliente se conecta al servidor.
2. Cliente genera mensaje incremental.
3. Cliente envía mensaje al servidor y espera mensaje de respuesta.
4. Servidor responde al mensaje.
5. Servidor desconecta al cliente.
6. Cliente verifica si aún debe enviar un mensaje y si es así, vuelve al paso 2.

### Ejemplo

Al ejecutar el comando `make docker-compose-up`  y luego  `make docker-compose-logs`, se observan los siguientes logs:

```
client1  | 2024-08-21 22:11:15 INFO     action: config | result: success | client_id: 1 | server_address: server:12345 | loop_amount: 5 | loop_period: 5s | log_level: DEBUG
client1  | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:14 DEBUG    action: config | result: success | port: 12345 | listen_backlog: 5 | logging_level: DEBUG
server   | 2024-08-21 22:11:14 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:15 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°1
server   | 2024-08-21 22:11:15 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:20 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:20 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°2
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°3
client1  | 2024-08-21 22:11:25 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°3
server   | 2024-08-21 22:11:25 INFO     action: accept_connections | result: in_progress
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:30 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:30 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°4
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: success | ip: 172.25.125.3
server   | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | ip: 172.25.125.3 | msg: [CLIENT 1] Message N°5
client1  | 2024-08-21 22:11:35 INFO     action: receive_message | result: success | client_id: 1 | msg: [CLIENT 1] Message N°5
server   | 2024-08-21 22:11:35 INFO     action: accept_connections | result: in_progress
client1  | 2024-08-21 22:11:40 INFO     action: loop_finished | result: success | client_id: 1
client1 exited with code 0
```


## Parte 1: Introducción a Docker
En esta primera parte del trabajo práctico se plantean una serie de ejercicios que sirven para introducir las herramientas básicas de Docker que se utilizarán a lo largo de la materia. El entendimiento de las mismas será crucial para el desarrollo de los próximos TPs.

### Ejercicio N°1:
Definir un script de bash `generar-compose.sh` que permita crear una definición de Docker Compose con una cantidad configurable de clientes.  El nombre de los containers deberá seguir el formato propuesto: client1, client2, client3, etc. 

El script deberá ubicarse en la raíz del proyecto y recibirá por parámetro el nombre del archivo de salida y la cantidad de clientes esperados:

`./generar-compose.sh docker-compose-dev.yaml 5`

Considerar que en el contenido del script pueden invocar un subscript de Go o Python:

```
#!/bin/bash
echo "Nombre del archivo de salida: $1"
echo "Cantidad de clientes: $2"
python3 mi-generador.py $1 $2
```

En el archivo de Docker Compose de salida se pueden definir volúmenes, variables de entorno y redes con libertad, pero recordar actualizar este script cuando se modifiquen tales definiciones en los sucesivos ejercicios.

### Ejercicio N°2:
Modificar el cliente y el servidor para lograr que realizar cambios en el archivo de configuración no requiera reconstruír las imágenes de Docker para que los mismos sean efectivos. La configuración a través del archivo correspondiente (`config.ini` y `config.yaml`, dependiendo de la aplicación) debe ser inyectada en el container y persistida por fuera de la imagen (hint: `docker volumes`).


### Ejercicio N°3:
Crear un script de bash `validar-echo-server.sh` que permita verificar el correcto funcionamiento del servidor utilizando el comando `netcat` para interactuar con el mismo. Dado que el servidor es un echo server, se debe enviar un mensaje al servidor y esperar recibir el mismo mensaje enviado.

En caso de que la validación sea exitosa imprimir: `action: test_echo_server | result: success`, de lo contrario imprimir:`action: test_echo_server | result: fail`.

El script deberá ubicarse en la raíz del proyecto. Netcat no debe ser instalado en la máquina _host_ y no se pueden exponer puertos del servidor para realizar la comunicación (hint: `docker network`). `


### Ejercicio N°4:
Modificar servidor y cliente para que ambos sistemas terminen de forma _graceful_ al recibir la signal SIGTERM. Terminar la aplicación de forma _graceful_ implica que todos los _file descriptors_ (entre los que se encuentran archivos, sockets, threads y procesos) deben cerrarse correctamente antes que el thread de la aplicación principal muera. Loguear mensajes en el cierre de cada recurso (hint: Verificar que hace el flag `-t` utilizado en el comando `docker compose down`).

## Parte 2: Repaso de Comunicaciones

Las secciones de repaso del trabajo práctico plantean un caso de uso denominado **Lotería Nacional**. Para la resolución de las mismas deberá utilizarse como base el código fuente provisto en la primera parte, con las modificaciones agregadas en el ejercicio 4.

### Ejercicio N°5:
Modificar la lógica de negocio tanto de los clientes como del servidor para nuestro nuevo caso de uso.

#### Cliente
Emulará a una _agencia de quiniela_ que participa del proyecto. Existen 5 agencias. Deberán recibir como variables de entorno los campos que representan la apuesta de una persona: nombre, apellido, DNI, nacimiento, numero apostado (en adelante 'número'). Ej.: `NOMBRE=Santiago Lionel`, `APELLIDO=Lorca`, `DOCUMENTO=30904465`, `NACIMIENTO=1999-03-17` y `NUMERO=7574` respectivamente.

Los campos deben enviarse al servidor para dejar registro de la apuesta. Al recibir la confirmación del servidor se debe imprimir por log: `action: apuesta_enviada | result: success | dni: ${DNI} | numero: ${NUMERO}`.



#### Servidor
Emulará a la _central de Lotería Nacional_. Deberá recibir los campos de la cada apuesta desde los clientes y almacenar la información mediante la función `store_bet(...)` para control futuro de ganadores. La función `store_bet(...)` es provista por la cátedra y no podrá ser modificada por el alumno.
Al persistir se debe imprimir por log: `action: apuesta_almacenada | result: success | dni: ${DNI} | numero: ${NUMERO}`.

#### Comunicación:
Se deberá implementar un módulo de comunicación entre el cliente y el servidor donde se maneje el envío y la recepción de los paquetes, el cual se espera que contemple:
* Definición de un protocolo para el envío de los mensajes.
* Serialización de los datos.
* Correcta separación de responsabilidades entre modelo de dominio y capa de comunicación.
* Correcto empleo de sockets, incluyendo manejo de errores y evitando los fenómenos conocidos como [_short read y short write_](https://cs61.seas.harvard.edu/site/2018/FileDescriptors/).


### Ejercicio N°6:
Modificar los clientes para que envíen varias apuestas a la vez (modalidad conocida como procesamiento por _chunks_ o _batchs_). 
Los _batchs_ permiten que el cliente registre varias apuestas en una misma consulta, acortando tiempos de transmisión y procesamiento.

La información de cada agencia será simulada por la ingesta de su archivo numerado correspondiente, provisto por la cátedra dentro de `.data/datasets.zip`.
Los archivos deberán ser inyectados en los containers correspondientes y persistido por fuera de la imagen (hint: `docker volumes`), manteniendo la convencion de que el cliente N utilizara el archivo de apuestas `.data/agency-{N}.csv` .

En el servidor, si todas las apuestas del *batch* fueron procesadas correctamente, imprimir por log: `action: apuesta_recibida | result: success | cantidad: ${CANTIDAD_DE_APUESTAS}`. En caso de detectar un error con alguna de las apuestas, debe responder con un código de error a elección e imprimir: `action: apuesta_recibida | result: fail | cantidad: ${CANTIDAD_DE_APUESTAS}`.

La cantidad máxima de apuestas dentro de cada _batch_ debe ser configurable desde config.yaml. Respetar la clave `batch: maxAmount`, pero modificar el valor por defecto de modo tal que los paquetes no excedan los 8kB. 

Por su parte, el servidor deberá responder con éxito solamente si todas las apuestas del _batch_ fueron procesadas correctamente.

### Ejercicio N°7:

Modificar los clientes para que notifiquen al servidor al finalizar con el envío de todas las apuestas y así proceder con el sorteo.
Inmediatamente después de la notificacion, los clientes consultarán la lista de ganadores del sorteo correspondientes a su agencia.
Una vez el cliente obtenga los resultados, deberá imprimir por log: `action: consulta_ganadores | result: success | cant_ganadores: ${CANT}`.

El servidor deberá esperar la notificación de las 5 agencias para considerar que se realizó el sorteo e imprimir por log: `action: sorteo | result: success`.
Luego de este evento, podrá verificar cada apuesta con las funciones `load_bets(...)` y `has_won(...)` y retornar los DNI de los ganadores de la agencia en cuestión. Antes del sorteo no se podrán responder consultas por la lista de ganadores con información parcial.

Las funciones `load_bets(...)` y `has_won(...)` son provistas por la cátedra y no podrán ser modificadas por el alumno.

No es correcto realizar un broadcast de todos los ganadores hacia todas las agencias, se espera que se informen los DNIs ganadores que correspondan a cada una de ellas.

## Parte 3: Repaso de Concurrencia
En este ejercicio es importante considerar los mecanismos de sincronización a utilizar para el correcto funcionamiento de la persistencia.

### Ejercicio N°8:

Modificar el servidor para que permita aceptar conexiones y procesar mensajes en paralelo. En caso de que el alumno implemente el servidor en Python utilizando _multithreading_,  deberán tenerse en cuenta las [limitaciones propias del lenguaje](https://wiki.python.org/moin/GlobalInterpreterLock).

## Condiciones de Entrega
Se espera que los alumnos realicen un _fork_ del presente repositorio para el desarrollo de los ejercicios y que aprovechen el esqueleto provisto tanto (o tan poco) como consideren necesario.

Cada ejercicio deberá resolverse en una rama independiente con nombres siguiendo el formato `ej${Nro de ejercicio}`. Se permite agregar commits en cualquier órden, así como crear una rama a partir de otra, pero al momento de la entrega deberán existir 8 ramas llamadas: ej1, ej2, ..., ej7, ej8.
 (hint: verificar listado de ramas y últimos commits con `git ls-remote`)

Se espera que se redacte una sección del README en donde se indique cómo ejecutar cada ejercicio y se detallen los aspectos más importantes de la solución provista, como ser el protocolo de comunicación implementado (Parte 2) y los mecanismos de sincronización utilizados (Parte 3).

Se proveen [pruebas automáticas](https://github.com/7574-sistemas-distribuidos/tp0-tests) de caja negra. Se exige que la resolución de los ejercicios pase tales pruebas, o en su defecto que las discrepancias sean justificadas y discutidas con los docentes antes del día de la entrega. El incumplimiento de las pruebas es condición de desaprobación, pero su cumplimiento no es suficiente para la aprobación. Respetar las entradas de log planteadas en los ejercicios, pues son las que se chequean en cada uno de los tests.

La corrección personal tendrá en cuenta la calidad del código entregado y casos de error posibles, se manifiesten o no durante la ejecución del trabajo práctico. Se pide a los alumnos leer atentamente y **tener en cuenta** los criterios de corrección informados  [en el campus](https://campusgrado.fi.uba.ar/mod/page/view.php?id=73393).
