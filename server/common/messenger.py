from .utils import Bet
from .serializer import Serializer

ACK_MESSAGE_OPCODE = 0
BATCH_ERROR_MESSAGE_OPCODE = 2

BET_PAYLOAD_SIZE = 144
OPCODE_SIZE = 2
CLIENT_ID_SIZE = 2
BET_AMOUNT_SIZE = 2

class Messenger:

    def __init__(self):
        self.serializer = Serializer()

    def read_message_opcode_and_client_id(self, connection) -> tuple:
        # Use __read_all to avoid short-reads
        opcode_bytes = self.__read_all(connection, OPCODE_SIZE)
        opcode = self.serializer.deserialize_int_to_bytes(opcode_bytes)
        client_id_bytes = self.__read_all(connection, CLIENT_ID_SIZE)
        client_id = self.serializer.deserialize_int_to_bytes(client_id_bytes)
        return opcode, client_id
    
    def read_bet_amount(self, connection) -> int:
        amount_bytes = self.__read_all(connection, BET_AMOUNT_SIZE)
        return self.serializer.deserialize_int_to_bytes(amount_bytes)
    
    def read_bet_batch_message(self, connection, bet_amount, agency_number) -> list[Bet]:
        bets = []
        for i in range (bet_amount):
            bet_bytes = self.__read_all(connection, BET_PAYLOAD_SIZE)
            bet = self.serializer.deserialize_bet(bet_bytes, agency_number)
            bets.append(bet)
        return bets
    
    def send_ack_message(self, connection):
        self.__write_all(connection, self.serializer.serialize_opcode(ACK_MESSAGE_OPCODE))

    def send_error_message(self, connection):
        self.__write_all(connection, self.serializer.serialize_opcode(BATCH_ERROR_MESSAGE_OPCODE))

    def __read_all(self, connection, size):
        # Ensures that exactly 'size' bytes are read from the connection
        buffer = b""
        while len(buffer) < size:
            chunk = connection.recv(size - len(buffer))
            if not chunk:
                raise ConnectionError("Connection closed before reading all data")
            buffer += chunk
        return buffer
    
    def __write_all(self, conn, data):
        # Ensures that all the bytes in 'data' are written to the connection
        total_sent = 0
        while total_sent < len(data):
            sent = conn.send(data[total_sent:])
            if sent == 0:
                raise ConnectionError("Connection closed before sending all data")
            total_sent += sent