import multiprocessing
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
        self.active_connections = []
        self._process_manager = None
        self._running = True

    def run(self):
        signal.signal(signal.SIGTERM, self.__exit_gracefully)
        self._process_manager = multiprocessing.Manager()
        while self._running:
            finished_clients = self._process_manager.list()
            store_lock = multiprocessing.Lock()
            processes = []

            for _ in range(self._client_amount):
                try: 
                    connection = self.__accept_new_connection()
                except OSError:
                    logging.error("action: accept_connections | result: fail | error: server socket has been closed")
                    return
                self.active_connections.append(connection)

                bet_transfer_process = multiprocessing.Process(target=self.__handle_client_connection, args=(connection, finished_clients, store_lock))
                bet_transfer_process.start()
                processes.append(bet_transfer_process)
            
            for process in processes:
                process.join()

            bets = load_bets()
            winners = [bet for bet in bets if has_won(bet)]
            logging.info(f'action: process_winners | result: success | total_winners: {len(winners)}')
            end_processes = []

            for client_id, c_connection in finished_clients:
                client_winners = [winner.number for winner in winners if winner.agency == client_id]
                send_winners_process = multiprocessing.Process(target=self.__send_winners_and_end_client_connection, args=(c_connection, client_winners))
                send_winners_process.start()
                end_processes.append(send_winners_process)

            for process in end_processes:
                process.join()

    def __exit_gracefully(self, sig, frame):
        self._running = False
        logging.info("action: shutdown | result: in_progress")
        self._server_socket.close()
        logging.info("action: close | result: success | resource type: server socket")

        for active_connection in self.active_connections:
            try:
                active_connection.close()
                logging.info(f"action: close | result: success | resource type: client socket | ip: {active_connection.getpeername()[0]}")
            except Exception as e:
                logging.error(f"action: close | result: fail | error: {e}")

        if self._process_manager is not None:
            self._process_manager.shutdown()
            logging.info("action: shutdown | result: success | resource type: process manager")

        logging.info("action: shutdown | result: success")
        
        

    def __handle_client_connection(self, connection, finished_clients, store_lock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        try:
            protocol_handler = ProtocolHandler(connection)
            client_id = protocol_handler.receive_and_store_bets(store_lock)
            finished_clients.append((client_id, connection))            
    
        except OSError as e:
           logging.error(f"action: receive_message | result: fail | error: {e}")
        except ConnectionError as e:
            logging.error(f"action: receive_message | result: fail | error: {e}")
                   
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

    def __send_winners_and_end_client_connection(self, connection, client_winners):
        ProtocolHandler(connection).send_winners(client_winners)
        logging.info(f"action: send_winners | result: success | winners: {client_winners}")
        connection.close()