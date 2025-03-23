from .utils import Bet
from .serializer import Serializer

ACK_MESSAGE_OPCODE = 0
BET_MESSAGE_SIZE = 150
OPCODE_SIZE = 2

class Messenger:

    def __init__(self):
        self.serializer = Serializer()

    def read_message_opcode(self, connection) -> int:
        # Use __read_all to avoid short-reads
        opcode_bytes = self.__read_all(connection, OPCODE_SIZE)
        return self.serializer.deserialize_opcode(opcode_bytes)
    
    def read_bet_message(self, connection) -> Bet:
        bet_bytes = self.__read_all(connection, BET_MESSAGE_SIZE - OPCODE_SIZE)
        return self.serializer.deserialize_bet(bet_bytes)
    
    def send_ack_message(self, connection):
        self.__write_all(connection, self.serializer.serialize_opcode(ACK_MESSAGE_OPCODE))

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