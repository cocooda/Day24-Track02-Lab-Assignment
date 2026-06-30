import json
from pathlib import Path

import pandas as pd

from src.encryption.vault import SimpleVault


def test_round_trip_decrypt_equals_original(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    payload = vault.encrypt_data("sensitive-medical-note")
    assert vault.decrypt_data(payload) == "sensitive-medical-note"


def test_ciphertext_does_not_contain_plaintext(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    payload = vault.encrypt_data("CCCD 012345678901")
    assert "012345678901" not in payload["ciphertext"]


def test_algorithm_is_aes_256_gcm(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    payload = vault.encrypt_data("hello")
    assert payload["algorithm"] == "AES-256-GCM"


def test_encrypted_dek_exists(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    payload = vault.encrypt_data("hello")
    assert payload["encrypted_dek"]


def test_encrypt_column_preserves_row_count_and_changes_values(tmp_path):
    vault = SimpleVault(master_key_path=str(tmp_path / ".vault_key"))
    df = pd.DataFrame({"cccd": ["012345678901", "123456789012"], "benh": ["A", "B"]})
    encrypted_df = vault.encrypt_column(df, "cccd")

    assert len(encrypted_df) == len(df)
    assert encrypted_df["cccd"].tolist() != df["cccd"].tolist()
    for value in encrypted_df["cccd"]:
        payload = json.loads(value)
        assert payload["algorithm"] == "AES-256-GCM"
