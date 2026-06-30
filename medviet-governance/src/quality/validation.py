from pathlib import Path

import pandas as pd

try:
    import great_expectations as gx
    from great_expectations.core.expectation_suite import ExpectationSuite
except Exception:  # pragma: no cover - optional runtime behavior
    gx = None
    ExpectationSuite = object


ALLOWED_DISEASES = {"Tiểu đường", "Huyết áp cao", "Tim mạch", "Khỏe mạnh"}


def _normalize_identifier(column: str, value: object) -> str:
    text = "" if value is None else str(value).strip()
    if not text:
        return text
    if column == "cccd" and text.isdigit():
        return text.zfill(12)
    if column == "so_dien_thoai" and text.isdigit():
        if len(text) == 9:
            return f"0{text}"
        return text.zfill(10)
    return text


def build_patient_expectation_suite():
    if gx is None:
        return {
            "expectation_suite_name": "patient_data_suite",
            "expectations": [
                "patient_id not null",
                "patient_id unique",
                "ket_qua_xet_nghiem between 0 and 50",
                "benh in allowed set",
            ],
        }

    try:
        return ExpectationSuite(expectation_suite_name="patient_data_suite")
    except TypeError:
        return ExpectationSuite("patient_data_suite")


def validate_anonymized_data(filepath: str) -> dict:
    anon_path = Path(filepath)
    df = pd.read_csv(anon_path)
    raw_path = Path("data/raw/patients_raw.csv")

    failed_checks: list[str] = []
    stats = {
        "total_rows": int(len(df)),
        "columns": list(df.columns),
    }

    important_columns = ["patient_id", "benh", "ket_qua_xet_nghiem"]
    if df[important_columns].isnull().any().any():
        failed_checks.append("important_columns_have_nulls")

    if not df["patient_id"].is_unique:
        failed_checks.append("patient_id_not_unique")

    if not df["benh"].isin(ALLOWED_DISEASES).all():
        failed_checks.append("benh_outside_allowed_set")

    numeric_results = pd.to_numeric(df["ket_qua_xet_nghiem"], errors="coerce")
    if numeric_results.isnull().any() or not numeric_results.between(0, 50).all():
        failed_checks.append("ket_qua_xet_nghiem_out_of_range")

    if raw_path.exists():
        raw_df = pd.read_csv(raw_path)
        stats["raw_rows"] = int(len(raw_df))
        if len(raw_df) != len(df):
            failed_checks.append("row_count_mismatch")

        for column in ["cccd", "so_dien_thoai", "email"]:
            raw_values = {_normalize_identifier(column, value) for value in raw_df[column].astype(str)}
            anon_values = {_normalize_identifier(column, value) for value in df[column].astype(str)}
            if raw_values & anon_values:
                failed_checks.append(f"raw_{column}_values_still_present")

    return {
        "success": not failed_checks,
        "failed_checks": failed_checks,
        "stats": stats,
    }
