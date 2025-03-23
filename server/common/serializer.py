from .utils import Bet


class Serializer:
    
    def serialize_opcode(self, opcode:int) -> bytes:
        # receives an integer and returns a byte array
        return self.__serialize_int_to_bytes(opcode, 2)
    
    def deserialize_opcode(self, opcodeBytes:bytes) -> int:
        # receives two bytes and parses into an integer
        return int.from_bytes(opcodeBytes, byteorder='big')
    

    def deserialize_bet(self, betBytes:bytes) -> Bet:
        # Receive a byte array and parse it into a Bet object
        agency_number = int.from_bytes(betBytes[:2], byteorder='big')
        document = int.from_bytes(betBytes[2:6], byteorder='big')
        number = int.from_bytes(betBytes[6:8], byteorder='big')
        birthdate = betBytes[8:18].decode('utf-8')
        first_name_len =  int.from_bytes(betBytes[18:20], byteorder='big')
        first_name = betBytes[20:20+first_name_len].decode('utf-8')
        last_name_len = int.from_bytes(betBytes[20+first_name_len: 22+first_name_len], byteorder='big')
        last_name = betBytes[22+first_name_len:22+first_name_len+last_name_len].decode('utf-8')
        
        return Bet(
            str(agency_number),
            first_name,
            last_name,
            str(document),
            birthdate,
            str(number)
        )
            
        
    def __serialize_int_to_bytes(self, number:int, size:int) -> bytes:
        # receives an integer and the number of bytes to represent it
        return number.to_bytes(size, byteorder='big')