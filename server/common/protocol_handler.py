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
        self.bet_batch_full_size = 0

    def receive_and_store_bets(self) ->bool:
        continue_loop = True
        opcode,agency_number = self.messenger.read_message_opcode_and_client_id(self.connection)
        active_connection_addr = self.connection.getpeername()
        logging.info(f'action: receive_message | result: success | client: {agency_number} |ip: {active_connection_addr[0]} | msg: {MESSAGES[opcode]}')
        
        if opcode == BET_BATCH_MESSAGE_OPCODE:
            bet_amount = self.messenger.read_bet_amount(self.connection) 
            if bet_amount > self.bet_batch_full_size:
                self.bet_batch_full_size = bet_amount
            if bet_amount < self.bet_batch_full_size:
                continue_loop = False
            try:
                bets = self.messenger.read_bet_batch_message(self.connection, bet_amount, agency_number)
                store_bets(bets)
                logging.info(f'action: apuesta_recibida | result: success | cantidad: {bet_amount}')
                self.messenger.send_ack_message(self.connection)

            except Exception as e:
                logging.error(f'result: fail | error: {e}')
                logging.error(f'action: apuesta_recibida | result: fail | cantidad: {bet_amount}')
                self.messenger.send_error_message(self.connection)

            return continue_loop
                