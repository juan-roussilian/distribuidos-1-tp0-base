
import logging
from .messenger import (
    ACK_MESSAGE_OPCODE,
    END_OF_BATCH_MESSAGE_OPCODE,
    BET_BATCH_MESSAGE_OPCODE,
    ASK_WINNERS_MESSAGE_OPCODE,
    WINNERS_MESSAGE_OPCODE,
    Messenger)
from .utils import load_bets, store_bets

MESSAGES = {
    ACK_MESSAGE_OPCODE: "ACK Message",
    BET_BATCH_MESSAGE_OPCODE: "Bet Batch Message",
    END_OF_BATCH_MESSAGE_OPCODE: "End of Batch Message",
    ASK_WINNERS_MESSAGE_OPCODE: "Ask Winners Message",
    WINNERS_MESSAGE_OPCODE: "Winners Message"
}
class ProtocolHandler:
    def __init__(self, connection):
        self.connection = connection
        self.messenger = Messenger()
        self.max_batch_size = 0

    def receive_and_store_bets(self, store_lock) -> int:
        while True:
            opcode, agency_number = self.messenger.read_message_opcode_and_client_id(self.connection)
            active_connection_addr = self.connection.getpeername()
            logging.info(f'action: receive_message | result: success | client: {agency_number} | ip: {active_connection_addr[0]} | msg: {MESSAGES[opcode]}')

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
                
                try:
                    with store_lock:
                        store_bets(bets)
                    
                    self.messenger.send_ack_message(self.connection)
                    logging.info(f'action: apuesta_recibida | result: success | cantidad: {bet_amount}')
                except Exception as e:
                    logging.error(f'Failed to store bets: {e}')
                    self.messenger.send_error_message(self.connection)  # Notify failure

            elif opcode == END_OF_BATCH_MESSAGE_OPCODE:
                logging.info(f'action: fin_lote | result: success | agencia: {agency_number}')
            elif opcode == ASK_WINNERS_MESSAGE_OPCODE:
                return agency_number
            
    def send_winners(self, winners):
        self.messenger.send_winners_message(self.connection, winners)