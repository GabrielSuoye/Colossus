from cryptography.fernet import Fernet, InvalidToken


class CryptoVault:
    def __init__(self, key_str: str):
        """
        Vault is initialized with a shared secret key.
        The key must be a base64url-encoded 32-byte string.
        """
        self.cipher = Fernet(key_str.encode())

    def encrypt_string(self, plaintext):
        # Converts plaintext into a secure, encrypted token string.
        if not plaintext:
            return ""
        encrypted_bytes = self.cipher.encrypt(
            plaintext.encode("utf-8")
        )  # Fernet requires bytes to work
        return encrypted_bytes.decode("utf-8")

    def decrypt_string(self, ciphertext: str) -> str:
        try:
            decrypted_bytes = self.cipher.decrypt(ciphertext.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except InvalidToken:
            return "[ERROR: Data Tampering Detected or Invalid Key]"
