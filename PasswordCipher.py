import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from User import User

class PasswordCipher:
    def __init__(self, user):
        salt = bytes(str(user.get_id()), "utf-8")
        key = bytes(user.get_key(), "utf-8")
        cipher_key = self.set_cipher_key(key, salt)
        self.__cipher = Fernet(cipher_key)

    def set_cipher_key(self, key, salt):
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=390000,
        )
        cipher_key = base64.urlsafe_b64encode(kdf.derive(key))
        return cipher_key

    def check_cipher(self, encrypted_password):
        try:
            self.decrypt_password(encrypted_password)
        except Exception as e:
            return False
        return True

    def encrypt_password(self, str_password):
        bytes_password = bytes(str_password, "utf-8")
        bytes_encrypted_password = self.__cipher.encrypt(bytes_password)
        str_encrypted_password = bytes_encrypted_password.decode("utf-8")
        return str_encrypted_password

    def decrypt_password(self, str_encrypted_password):
        bytes_encrypted_password = bytes(str_encrypted_password, "utf-8")
        bytes_password = self.__cipher.decrypt(bytes_encrypted_password)
        str_password = bytes_password.decode("utf-8")
        return str_password
