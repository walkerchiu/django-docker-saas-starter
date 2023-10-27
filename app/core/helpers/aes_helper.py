import base64

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from urllib.parse import quote, unquote


class AESHelper:
    def __init__(self, key: str, iv: str):
        self.key = key.encode("utf-8")
        self.iv = iv.encode("utf-8")

    def encrypt_data(self, data):
        data = quote(data)
        data = data.encode("utf-8")
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        ct_bytes = cipher.encrypt(pad(data, AES.block_size))
        ct_base64 = base64.b64encode(ct_bytes).decode("utf-8")

        return ct_base64

    def decrypt_data(self, data):
        ct_bytes = base64.b64decode(data)
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        pt_bytes = unpad(cipher.decrypt(ct_bytes), AES.block_size)
        pt = pt_bytes.decode("utf-8")
        pt = unquote(pt)

        return pt
