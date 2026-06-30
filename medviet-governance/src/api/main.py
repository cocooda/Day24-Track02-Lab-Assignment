from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI

from src.access.rbac import get_current_user, require_permission
from src.pii.anonymizer import MedVietAnonymizer


app = FastAPI(title="MedViet Data API", version="1.0.0")
anonymizer = MedVietAnonymizer()
RAW_DATA_PATH = Path("data/raw/patients_raw.csv")


def _load_raw_patients() -> pd.DataFrame:
    return pd.read_csv(RAW_DATA_PATH)


@app.get("/api/patients/raw")
@require_permission(resource="patient_data", action="read")
async def get_raw_patients(current_user: dict = Depends(get_current_user)):
    df = _load_raw_patients()
    return df.head(10).to_dict(orient="records")


@app.get("/api/patients/anonymized")
@require_permission(resource="training_data", action="read")
async def get_anonymized_patients(current_user: dict = Depends(get_current_user)):
    df = _load_raw_patients()
    df_anon = anonymizer.anonymize_dataframe(df)
    return df_anon.head(10).to_dict(orient="records")


@app.get("/api/metrics/aggregated")
@require_permission(resource="aggregated_metrics", action="read")
async def get_aggregated_metrics(current_user: dict = Depends(get_current_user)):
    df = _load_raw_patients()
    disease_counts = df["benh"].value_counts().sort_index().to_dict()
    return {"disease_counts": disease_counts, "total_records": int(len(df))}


@app.delete("/api/patients/{patient_id}")
@require_permission(resource="patient_data", action="delete")
async def delete_patient(patient_id: str, current_user: dict = Depends(get_current_user)):
    return {
        "deleted": True,
        "patient_id": patient_id,
        "deleted_by": current_user["username"],
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "MedViet Data API"}
