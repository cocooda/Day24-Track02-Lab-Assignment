import pandas as pd
import pytest
from pathlib import Path

from src.pii.anonymizer import MedVietAnonymizer


RAW_PATH = Path("data/raw/patients_raw.csv")
PROCESSED_PATH = Path("data/processed/patients_anonymized.csv")


@pytest.fixture(scope="module")
def anonymizer():
    return MedVietAnonymizer()


@pytest.fixture(scope="module")
def sample_df():
    return pd.read_csv(RAW_PATH).head(50)


class TestPIIDetection:
    def test_cccd_detected(self, anonymizer):
        text = "Bệnh nhân Nguyen Van A, CCCD: 012345678901"
        results = anonymizer.analyzer.analyze(
            text=text,
            language="vi",
            entities=["VN_CCCD"],
        )
        assert any(result.entity_type == "VN_CCCD" for result in results)

    def test_phone_detected(self, anonymizer):
        text = "Liên hệ: 0912345678"
        results = anonymizer.analyzer.analyze(
            text=text,
            language="vi",
            entities=["VN_PHONE"],
        )
        assert any(result.entity_type == "VN_PHONE" for result in results)

    def test_email_detected(self, anonymizer):
        text = "Email: nguyenvana@gmail.com"
        results = anonymizer.analyzer.analyze(
            text=text,
            language="vi",
            entities=["EMAIL_ADDRESS"],
        )
        assert any(result.entity_type == "EMAIL_ADDRESS" for result in results)

    def test_person_detected(self, anonymizer):
        text = "Bệnh nhân là Nguyễn Văn An"
        results = anonymizer.analyzer.analyze(
            text=text,
            language="vi",
            entities=["PERSON"],
        )
        assert any(result.entity_type == "PERSON" for result in results)

    def test_detection_rate_above_95_percent(self, anonymizer, sample_df):
        pii_columns = ["ho_ten", "cccd", "so_dien_thoai", "email"]
        rate = anonymizer.calculate_detection_rate(sample_df, pii_columns)
        assert rate >= 0.95, f"Detection rate {rate:.2%} < 95%"


class TestAnonymization:
    def test_pii_not_in_output(self, anonymizer, sample_df):
        df_anon = anonymizer.anonymize_dataframe(sample_df)

        assert not set(sample_df["cccd"].astype(str)) & set(df_anon["cccd"].astype(str))
        assert not set(sample_df["so_dien_thoai"].astype(str)) & set(
            df_anon["so_dien_thoai"].astype(str)
        )
        assert not set(sample_df["email"].astype(str)) & set(df_anon["email"].astype(str))

    def test_non_pii_columns_unchanged(self, anonymizer, sample_df):
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        pd.testing.assert_series_equal(sample_df["benh"], df_anon["benh"], check_names=False)
        pd.testing.assert_series_equal(
            sample_df["ket_qua_xet_nghiem"],
            df_anon["ket_qua_xet_nghiem"],
            check_names=False,
        )

    def test_patient_id_unchanged(self, anonymizer, sample_df):
        df_anon = anonymizer.anonymize_dataframe(sample_df)
        pd.testing.assert_series_equal(
            sample_df["patient_id"],
            df_anon["patient_id"],
            check_names=False,
        )

    def test_processed_csv_exists_after_anonymization(self, anonymizer, sample_df):
        anonymizer.anonymize_dataframe(sample_df)
        assert PROCESSED_PATH.exists()
