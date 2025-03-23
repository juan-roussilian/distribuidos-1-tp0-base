import logging
from .messenger import Messenger
from .utils import store_bets

BET_MESSAGE_OPCODE = 1


MESSAGES = {
    0: "ACK Message",
    1: "Bet Message"
}

class ProtocolHandler:

    def __init__(self, connection):
        self.messenger = Messenger()
        self.connection = connection

    def receive_and_store_bet(self):
        opcode = self.messenger.read_message_opcode(self.connection)
        active_connection_addr = self.connection.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {active_connection_addr[0]} | msg: {MESSAGES[opcode]}')
        
        if opcode == BET_MESSAGE_OPCODE:
            bet = self.messenger.read_bet_message(self.connection)
            store_bets([bet])
            logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
            self.messenger.send_ack_message(self.connection)
                