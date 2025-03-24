import logging
from .messenger import Messenger
from .utils import store_bets

BET_BATCH_MESSAGE_OPCODE = 1


MESSAGES = {
    0: "ACK Message",
    1: "Bet Batch Message"
}

class ProtocolHandler:

    def __init__(self, connection):
        self.messenger = Messenger()
        self.connection = connection

    def receive_and_store_bets(self):
        opcode,client_id = self.messenger.read_message_opcode_and_client_id(self.connection)
        active_connection_addr = self.connection.getpeername()
        logging.info(f'action: receive_message | result: success | client: {client_id} |ip: {active_connection_addr[0]} | msg: {MESSAGES[opcode]}')
        
        if opcode == BET_BATCH_MESSAGE_OPCODE:
            bet_amount = self.messenger.read_bet_amount(self.connection) 
            try:
                bets = self.messenger.read_bet_batch_message(self.connection, bet_amount)
                store_bets(bets)
                logging.info(f'action: apuesta_recibida | result: success | cantidad: {bet_amount}')
                self.messenger.send_ack_message(self.connection)
            except:
                logging.error(f'action: apuesta_recibida | result: fail | cantidad: {bet_amount}')
                