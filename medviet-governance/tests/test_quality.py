from pathlib import Path

from src.pii.anonymizer import MedVietAnonymizer
from src.quality.validation import validate_anonymized_data


def test_validate_anonymized_data_success():
    anonymizer = MedVietAnonymizer()
    raw_path = Path("data/raw/patients_raw.csv")
    df = __import__("pandas").read_csv(raw_path)
    anonymizer.anonymize_dataframe(df)

    result = validate_anonymized_data("data/processed/patients_anonymized.csv")

    assert result["success"] is True
    assert result["failed_checks"] == []
    assert result["stats"]["total_rows"] == len(df)


def test_validate_anonymized_data_reports_stats():
    result = validate_anonymized_data("data/processed/patients_anonymized.csv")
    assert "columns" in result["stats"]
    assert "total_rows" in result["stats"]
