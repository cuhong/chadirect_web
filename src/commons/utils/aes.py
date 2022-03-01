# # http://redutan.github.io/2015/11/20/about-crypto
# # https://perfectacle.github.io/2019/11/24/aes/
#
# import base64
#
# from Crypto import Random
# from Crypto.Cipher import AES
#
#
# class AES256Cipher(object):
#
#     def __init__(self, key):
#         self.bs = AES.block_size
#         self.key = bytes(key, 'utf-8')
#
#     def pad(self, s: str):
#         return bytes(s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), 'utf-8')
#
#     def unpad(self, s):
#         return s[:-ord(s[len(s) - 1:])]
#
#     def _encrypt(self, message: str):
#         raw = self.pad(message)
#         iv = self.key[:self.bs]
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         return iv + cipher.encrypt(raw)
#
#     def encrypt(self, message: str):
#         _encrypt = self._encrypt(message)
#         return base64.b64encode(_encrypt)
#
#     def encrypt_string(self, message: str):
#         _encrypt = self._encrypt(message)
#         return base64.b64encode(_encrypt).decode('utf-8')
#
#     def decrypt(self, enc: str):
#         message = base64.b64decode(enc)
#         iv = message[:self.bs]
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         return self.unpad(cipher.decrypt(message[AES.block_size:])).decode('utf-8')
#
#
# #
# #
# # key = "Zq4t7w!z%C*F-JaNdRgUkXn2r5u8x/A?"
# # #
# # aes = AES256Cipher(key)
# # msg = "#test@12345"
# #
# # enc = aes.encrypt_string(msg)
# # print(enc)
# # dec = aes.decrypt(enc)
# # print(dec)
# # # bs = 128
# # # msg = "테스트"
# # # s = msg.encode('utf8')
# # #
# # # type(chr(bs - len(s) % bs))
# #
# #
# # from hashlib import sha256
# # import base64
# # from Crypto import Random
# # from Crypto.Cipher import AES
# #
# #
# #
# # class AESCipher:
# #
# #     def __init__(self, key):
# #         self.bs = 16
# #         self.key = bytes(key, 'utf-8')
# #
# #     def pad(self, s):
# #         return bytes(s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), 'utf-8')
# #
# #     def unpad(self, s):
# #         return s[0:-ord(s[-1:])]
# #
# #     def encrypt(self, raw):
# #         raw = self.pad(raw)
# #         iv = "encryptionIntVec".encode('utf-8')
# #         cipher = AES.new(self.key, AES.MODE_CBC, iv)
# #         return base64.b64encode(iv + cipher.encrypt(raw))
# #
# #     def decrypt(self, enc):
# #         enc = base64.b64decode(enc)
# #         iv = enc[:16]
# #         cipher = AES.new(self.key, AES.MODE_CBC, iv)
# #         return self.unpad(cipher.decrypt(enc[16:])).decode('utf8')
#
# # cipher = AESCipher('enIntVecTest2020')
# # encrypted = cipher.encrypt('#test@12345')
# # decrypted = cipher.decrypt(encrypted)
# #
# # print(encrypted)
# # # b'ZW5jcnlwdGlvbkludFZlY5R4atTszEmJ4/tF8YjcyoU='
# #
# #
# # import base64
# # from Crypto.Cipher import AES
# #
# # BS = 16
# # pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
# # unpad = lambda s : s[0:-ord(s[-1:])]
# # class AESCipher:
# #
# #     def __init__( self, key ):
# #         self.key = bytes(key, 'utf-8')
# #
# #     def encrypt( self, raw ):
# #         raw = pad(raw)
# #         iv = "encryptionIntVec".encode('utf-8')
# #         cipher = AES.new(self.key, AES.MODE_CBC, iv )
# #         return base64.b64encode(cipher.encrypt( raw ) )
# #     def decrypt( self, enc ):
# #         iv = "encryptionIntVec".encode('utf-8')
# #         enc = base64.b64decode(enc)
# #         cipher = AES.new(self.key, AES.MODE_CBC, iv )
# #         return unpad(cipher.decrypt( enc )).decode('utf8')
# # cipher = AESCipher('enIntVecTest2020')
# # encrypted = cipher.encrypt('#test@12345')
# # print(encrypted.decode('utf-8'))
# # # -> lHhq1OzMSYnj+0XxiNzKhQ==
# # decrypted = cipher.decrypt(encrypted)
# # print(decrypted)
# # # -> #test@12345