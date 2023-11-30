import hashlib
import binascii
import base64
class EncryptionUtil:
    
    @staticmethod
    def ComputeSHA256Bytes(input:bytes) -> bytes:       
        m = hashlib.sha256()
        m.update(input)
        return m.digest()
    