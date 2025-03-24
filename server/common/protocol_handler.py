import logging
from .messenger import (
    ACK_MESSAGE_OPCODE,
    END_OF_BATCH_MESSAGE_OPCODE,
    BET_BATCH_MESSAGE_OPCODE,
    Messenger)
from .utils import store_bets


MESSAGES = {
    ACK_MESSAGE_OPCODE: "ACK Message",
    BET_BATCH_MESSAGE_OPCODE: "Bet Batch Message",
    END_OF_BATCH_MESSAGE_OPCODE: "End of Batch Message"

}

class ProtocolHandler:

    def __init__(self, connection):
        self.messenger = Messenger()
        self.connection = connection
        self.max_batch_size = 0
    def receive_and_store_bets(self):

        while True:
            opcode,agency_number = self.messenger.read_message_opcode_and_client_id(self.connection)
            active_connection_addr = self.connection.getpeername()
            logging.info(f'action: receive_message | result: success | client: {agency_number} |ip: {active_connection_addr[0]} | msg: {MESSAGES[opcode]}')
            
            if opcode == BET_BATCH_MESSAGE_OPCODE:
                bet_amount = self.messenger.read_bet_amount(self.connection) 
                if bet_amount > self.max_batch_size:
                    self.max_batch_size = bet_amount
                try:
                    bets = self.messenger.read_bet_batch_message(self.connection, bet_amount, agency_number)
                except Exception as e:
                    logging.error(f'result: fail | error: {e}')
                    logging.error(f'action: apuesta_recibida | result: fail | cantidad: {bet_amount}')
                    self.messenger.send_error_message(self.connection) 
                    return
                    
                store_bets(bets)
                logging.info(f'action: apuesta_recibida | result: success | cantidad: {bet_amount}')
                self.messenger.send_ack_message(self.connection)

            elif opcode == END_OF_BATCH_MESSAGE_OPCODE:
                logging.info(f'action: fin_lote | result: success | agencia: {agency_number}')
                return
