import base64
import json
import os
from pathlib import Path

import pandas as pd
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class SimpleVault:
    def __init__(self, master_key_path: str = ".vault_key"):
        self.master_key_path = Path(master_key_path)
        self.kek = self._load_or_create_kek()

    def _load_or_create_kek(self) -> bytes:
        if self.master_key_path.exists():
            return base64.b64decode(self.master_key_path.read_bytes())

        kek = os.urandom(32)
        self.master_key_path.write_bytes(base64.b64encode(kek))
        return kek

    def generate_dek(self) -> tuple[bytes, bytes]:
        plaintext_dek = os.urandom(32)
        nonce = os.urandom(12)
        encrypted_dek = nonce + AESGCM(self.kek).encrypt(nonce, plaintext_dek, None)
        return plaintext_dek, encrypted_dek

    def decrypt_dek(self, encrypted_dek: bytes) -> bytes:
        nonce = encrypted_dek[:12]
        ciphertext = encrypted_dek[12:]
        return AESGCM(self.kek).decrypt(nonce, ciphertext, None)

    def encrypt_data(self, plaintext: str) -> dict:
        plaintext_dek, encrypted_dek = self.generate_dek()
        nonce = os.urandom(12)
        ciphertext = AESGCM(plaintext_dek).encrypt(nonce, plaintext.encode("utf-8"), None)
        del plaintext_dek
        return {
            "encrypted_dek": base64.b64encode(encrypted_dek).decode("utf-8"),
            "ciphertext": base64.b64encode(nonce + ciphertext).decode("utf-8"),
            "algorithm": "AES-256-GCM",
        }

    def decrypt_data(self, encrypted_payload: dict) -> str:
        encrypted_dek = base64.b64decode(encrypted_payload["encrypted_dek"])
        ciphertext_with_nonce = base64.b64decode(encrypted_payload["ciphertext"])
        plaintext_dek = self.decrypt_dek(encrypted_dek)
        nonce = ciphertext_with_nonce[:12]
        ciphertext = ciphertext_with_nonce[12:]
        plaintext = AESGCM(plaintext_dek).decrypt(nonce, ciphertext, None)
        del plaintext_dek
        return plaintext.decode("utf-8")

    def encrypt_column(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        encrypted_df = df.copy()
        encrypted_df[column] = encrypted_df[column].apply(
            lambda value: json.dumps(self.encrypt_data(str(value)))
        )
        return encrypted_df
