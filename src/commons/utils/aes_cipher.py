# https://stackoverflow.com/questions/49767968/pycryprodome-aes-cbc-mismatch-after-decryption-in-python
import base64
import secrets
from typing import Optional

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import urllib


class AESCipherError(Exception):
    def __init__(self, msg):
        self.msg = msg


class AESCipher:
    def __init__(self, key: str, iv: Optional[str] = None):
        try:
            self.key = key
            self.key_byte = self.string_to_byte(key)
            self.iv = bytes([0x00] * 16)
        except Exception as e:
            raise AESCipherError('비밀키(및 Initial Vector) 값을 확인하세요.')

    @classmethod
    def generate_key(cls) -> str:
        key = secrets.token_urlsafe(nbytes=32)
        key = base64.b64encode(key.encode()).decode()
        return key[:32]

    @classmethod
    def string_to_byte(cls, string: str) -> bytes:
        return bytes(string, encoding="raw_unicode_escape")

    def encrypt(self, data: str) -> bytes:
        try:
            data = data.encode('UTF-8')
            data = pad(data, AES.block_size)
            encryptor = AES.new(self.key_byte, AES.MODE_CBC, IV=self.iv)
            ciphertext = encryptor.encrypt(data)
            return ciphertext
        except Exception as e:
            raise AESCipherError(f'암호화 실패 : {str(e)}')

    def encrypt_to_string(self, data: str) -> str:
        try:
            byte_ciphertext = self.encrypt(data)
            return base64.b64encode(byte_ciphertext).decode('utf-8')
        except Exception as e:
            raise AESCipherError(f'암호화 실패 : {str(e)}')

    def decrypt(self, encrypted_string: str) -> bytes:
        try:
            data = base64.b64decode(encrypted_string)
            decryptor = AES.new(self.key_byte, AES.MODE_CBC, IV=self.iv)
            plaintext = decryptor.decrypt(data)
            return unpad(plaintext, AES.block_size)
        except Exception as e:
            raise AESCipherError(f'복호화 실패 : {str(e)}')

    def decrypt_to_string(self, encrypted_string: str) -> str:
        try:
            decrypted_byte = self.decrypt(encrypted_string)
            return decrypted_byte.decode('utf-8')
        except Exception as e:
            raise AESCipherError(f'복호화 실패 : {str(e)}')
