from .utils import Bet


class Serializer:
    
    def serialize_opcode(self, opcode:int) -> bytes:
        return self.serialize_int_to_bytes(opcode, 2)
    
    def deserialize_int_to_bytes(self, bytes:bytes) -> int:
        return int.from_bytes(bytes, byteorder='big')
    
    def deserialize_bet(self, betBytes:bytes, agency_number:int) -> Bet:
        document = int.from_bytes(betBytes[0:4], byteorder='big')
        number = int.from_bytes(betBytes[4:6], byteorder='big')
        birthdate = betBytes[6:16].decode('utf-8')
        first_name_len =  int.from_bytes(betBytes[16:18], byteorder='big')
        first_name = betBytes[18:18+first_name_len].decode('utf-8')
        last_name_len = int.from_bytes(betBytes[18+first_name_len: 20+first_name_len], byteorder='big')
        last_name = betBytes[20+first_name_len:20+first_name_len+last_name_len].decode('utf-8')
        
        return Bet(
            str(agency_number),
            first_name,
            last_name,
            str(document),
            birthdate,
            str(number)
        )
            
    def serialize_int_to_bytes(self, number:int, size:int) -> bytes:
        return number.to_bytes(size, byteorder='big')