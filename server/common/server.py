import signal
import socket
import logging
from .protocol_handler import ProtocolHandler


class Server:


    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.active_connection = None

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
            if self.active_connection is not None:
                self.active_connection.close()
                logging.info(f'action: close | result: success | resource type: client socket | ip: {self.self.active_connection.getpeername()[0]}')
            quit()
        return sigterm_handler

    def __handle_client_connection(self):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            while True:
                protocol_handler = ProtocolHandler(self.active_connection)
                protocol_handler.receive_and_store_bets()
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
