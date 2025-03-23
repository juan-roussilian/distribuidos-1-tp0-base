import signal
import socket
import logging
from .serializer import Serializer  
from .utils import store_bets

BET_MESSAGE_OPCODE = 1
MESSAGES = {
    0: "ACK Message",
    1: "Bet Message"
}

class Server:


    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        signal.signal(signal.SIGTERM, self.__exit_gracefully())
        while True:
            self.active_connection = self.__accept_new_connection()
            self.__handle_client_connection()

    def __exit_gracefully(self):
        def sigterm_handler(sig, frame):
            self._server_socket.close()
            logging.info(f'action: close | result: success | resource type: server socket')
            self.active_connection.close()
            logging.info(f'action: close | result: success | resource type: client socket | ip: {self.active_connection_addr[0]}')
            quit()
        return sigterm_handler
    
    def __read_all(self, conn, size):
        """
        Ensures that exactly 'size' bytes are read from the connection.
        """
        buffer = b""
        while len(buffer) < size:
            chunk = conn.recv(size - len(buffer))
            if not chunk:
                raise ConnectionError("Connection closed before reading all data")
            buffer += chunk
        return buffer
    
    def __write_all(self, conn, data):
        """
        Ensures that all the bytes in 'data' are written to the connection.
        """
        total_sent = 0
        while total_sent < len(data):
            sent = conn.send(data[total_sent:])
            if sent == 0:
                raise ConnectionError("Connection closed before sending all data")
            total_sent += sent

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            serializer = Serializer()
            # Use __read_all to avoid short-reads
            opcode_bytes = self.__read_all(self.active_connection, 2)
            opcode = serializer.deserialize_opcode(opcode_bytes)
            self.active_connection_addr = self.active_connection.getpeername()
            logging.info(f'action: receive_message | result: success | ip: {self.active_connection_addr[0]} | msg: {MESSAGES[opcode]}')

            if opcode == BET_MESSAGE_OPCODE:
                bet_bytes = self.__read_all(self.active_connection, 148)
                bet = serializer.deserialize_bet(bet_bytes)
                store_bets([bet])
                logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
                self.__write_all(self.active_connection, serializer.serialize_opcode(0))

                
        except OSError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        except ConnectionError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
        finally:
            self.active_connection.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        c, addr = self._server_socket.accept()
        logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
        return c
