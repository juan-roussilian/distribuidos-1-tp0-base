import signal
import socket
import logging
from .utils import has_won, load_bets
from .protocol_handler import ProtocolHandler


class Server:


    def __init__(self, port, listen_backlog, client_amount):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self._client_amount = client_amount
        self._finished_clients = []
        self.active_connections = []

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """

        signal.signal(signal.SIGTERM, self.__exit_gracefully())
        while len(self._finished_clients) < self._client_amount:
            connection = self.__accept_new_connection()
            self.active_connections.append(connection)  
            client_id = self.__handle_client_connection(connection)
            self._finished_clients.append((client_id, connection))
             
        bets = load_bets()
        winners = []
        for bet in bets:
            if has_won(bet):
                winners.append(bet)
        for client_id, c_connection in self._finished_clients:
            client_winners = [winner.number for winner in winners if winner.agency == client_id]
            self.__end_client_connection(c_connection, client_winners)
    def __exit_gracefully(self):
        def sigterm_handler(sig, frame):
            self._server_socket.close()
            logging.info(f'action: close | result: success | resource type: server socket')
            for active_connection in self.active_connections:
                active_connection.close()
                logging.info(f'action: close | result: success | resource type: client socket | ip: {active_connection.getpeername()[0]}')
            quit()
        return sigterm_handler

    def __handle_client_connection(self, connection) -> int:
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            protocol_handler = ProtocolHandler(connection)
            return protocol_handler.receive_and_store_bets()

        except OSError as e:
           logging.error(f"action: receive_message | result: fail | error: {e}")
        except ConnectionError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
            
    def __end_client_connection(self, connection, client_winners):
        ProtocolHandler(connection).send_winners(client_winners)
        logging.info(f"action: send_winners | result: success | winners: {client_winners}")
        connection.close()        
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
