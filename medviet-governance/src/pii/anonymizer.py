import re
import hashlib
import secrets
from pathlib import Path

import pandas as pd

from .detector import VN_CCCD_REGEX, VN_PHONE_REGEX, build_vietnamese_analyzer, detect_pii

_rng = secrets.SystemRandom()
EMAIL_REGEX = re.compile(r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")

try:
    from faker import Faker

    fake = Faker("vi_VN")
    Faker.seed(42)
except ModuleNotFoundError:
    class _FallbackFake:
        def __init__(self):
            self._counter = 0
            self._first_names = [
                "Nguyen",
                "Tran",
                "Le",
                "Pham",
                "Hoang",
                "Phan",
                "Vu",
                "Dang",
            ]
            self._middle_names = ["Van", "Thi", "Minh", "Ngoc", "Duc", "Anh"]
            self._last_names = ["An", "Binh", "Chau", "Dung", "Giang", "Hanh", "Khanh", "Linh"]
            self._streets = ["Le Loi", "Nguyen Hue", "Tran Hung Dao", "Hai Ba Trung"]
            self._cities = ["Ha Noi", "Da Nang", "Ho Chi Minh"]

        def _pick(self, values: list[str]) -> str:
            digest = hashlib.sha256(f"fallback-{self._counter}".encode("utf-8")).digest()
            self._counter += 1
            return values[int.from_bytes(digest[:4], "big") % len(values)]

        def _number(self, start: int, end: int) -> int:
            digest = hashlib.sha256(f"fallback-num-{self._counter}".encode("utf-8")).digest()
            self._counter += 1
            span = end - start + 1
            return start + (int.from_bytes(digest[:4], "big") % span)

        def name(self) -> str:
            return " ".join(
                [
                    self._pick(self._first_names),
                    self._pick(self._middle_names),
                    self._pick(self._last_names),
                ]
            )

        def email(self) -> str:
            local = f"user{self._number(1000, 9999)}"
            domain = self._pick(["example.com", "medviet.vn", "mail.vn"])
            return f"{local}@{domain}"

        def address(self) -> str:
            number = self._number(1, 250)
            street = self._pick(self._streets)
            city = self._pick(self._cities)
            return f"{number} {street}, {city}"

    fake = _FallbackFake()


class MedVietAnonymizer:
    def __init__(self):
        self.analyzer = build_vietnamese_analyzer()

    @staticmethod
    def _fake_cccd() -> str:
        return "".join(str(_rng.randint(0, 9)) for _ in range(12))

    @staticmethod
    def _fake_phone() -> str:
        prefix = str(_rng.choice([3, 5, 7, 8, 9]))
        return f"0{prefix}{''.join(str(_rng.randint(0, 9)) for _ in range(8))}"

    @staticmethod
    def _mask_value(value: str) -> str:
        if not value:
            return value
        if "@" in value:
            local, domain = value.split("@", 1)
            masked_local = (local[:1] + "*" * max(len(local) - 1, 0)) if local else "***"
            return f"{masked_local}@{domain}"
        if value.isdigit():
            return "*" * max(len(value) - 4, 0) + value[-4:]

        tokens = value.split()
        masked_tokens = []
        for token in tokens:
            if len(token) <= 1:
                masked_tokens.append(token)
            elif len(token) == 2:
                masked_tokens.append(token[0] + "*")
            else:
                masked_tokens.append(token[0] + "*" * (len(token) - 2) + token[-1])
        return " ".join(masked_tokens)

    @staticmethod
    def _hash_value(value: str) -> str:
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _generalize_date(value: str) -> str:
        text = str(value).strip()
        if not text:
            return text
        for separator in ("/", "-"):
            parts = text.split(separator)
            if len(parts) == 3 and len(parts[-1]) == 4:
                return parts[-1]
        return text[-4:] if len(text) >= 4 else text

    def _replacement_for(self, entity_type: str, original: str) -> str:
        if entity_type == "PERSON":
            replacement = fake.name()
            while replacement == original:
                replacement = fake.name()
            return replacement
        if entity_type == "EMAIL_ADDRESS":
            replacement = fake.email()
            while replacement == original:
                replacement = fake.email()
            return replacement
        if entity_type == "VN_CCCD":
            replacement = self._fake_cccd()
            while replacement == original:
                replacement = self._fake_cccd()
            return replacement
        if entity_type == "VN_PHONE":
            replacement = self._fake_phone()
            while replacement == original:
                replacement = self._fake_phone()
            return replacement
        return original

    @staticmethod
    def _normalize_for_detection(column: str, value: object) -> str:
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

    def anonymize_text(self, text: str, strategy: str = "replace") -> str:
        normalized = "" if text is None else str(text)
        results = detect_pii(normalized, self.analyzer)
        if not results:
            return normalized

        transformed = normalized
        for result in sorted(results, key=lambda item: item.start, reverse=True):
            original = transformed[result.start:result.end]
            if strategy == "replace":
                replacement = self._replacement_for(result.entity_type, original)
            elif strategy == "mask":
                replacement = self._mask_value(original)
            elif strategy == "hash":
                replacement = self._hash_value(original)
            elif strategy == "generalize":
                replacement = self._generalize_date(original)
            else:
                raise ValueError(f"Unsupported anonymization strategy: {strategy}")
            transformed = transformed[: result.start] + replacement + transformed[result.end :]
        return transformed

    def anonymize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        df_anon = df.copy()
        original_cccds = {
            self._normalize_for_detection("cccd", value) for value in df["cccd"].astype(str)
        }
        original_phones = {
            self._normalize_for_detection("so_dien_thoai", value)
            for value in df["so_dien_thoai"].astype(str)
        }
        original_emails = set(df["email"].astype(str))
        used_cccds: set[str] = set()
        used_phones: set[str] = set()
        used_emails: set[str] = set()

        def next_unique(generator, disallowed: set[str], used: set[str]) -> str:
            candidate = generator()
            while candidate in disallowed or candidate in used:
                candidate = generator()
            used.add(candidate)
            return candidate

        df_anon["ho_ten"] = df_anon["ho_ten"].astype(str).apply(
            lambda value: self.anonymize_text(value, strategy="replace")
        )
        df_anon["cccd"] = df_anon["cccd"].astype(str).apply(
            lambda _: next_unique(self._fake_cccd, original_cccds, used_cccds)
        )
        df_anon["ngay_sinh"] = df_anon["ngay_sinh"].astype(str).apply(self._generalize_date)
        df_anon["so_dien_thoai"] = df_anon["so_dien_thoai"].astype(str).apply(
            lambda _: next_unique(self._fake_phone, original_phones, used_phones)
        )
        df_anon["email"] = df_anon["email"].astype(str).apply(
            lambda _: next_unique(fake.email, original_emails, used_emails)
        )
        df_anon["dia_chi"] = df_anon["dia_chi"].astype(str).apply(lambda _: fake.address())
        df_anon["bac_si_phu_trach"] = df_anon["bac_si_phu_trach"].astype(str).apply(
            lambda value: self.anonymize_text(value, strategy="replace")
        )

        output_path = Path("data/processed/patients_anonymized.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df_anon.to_csv(output_path, index=False)
        return df_anon

    def calculate_detection_rate(
        self,
        original_df: pd.DataFrame,
        pii_columns: list,
    ) -> float:
        entity_map = {
            "ho_ten": "PERSON",
            "cccd": "VN_CCCD",
            "so_dien_thoai": "VN_PHONE",
            "email": "EMAIL_ADDRESS",
        }
        total = 0
        detected = 0
        for column in pii_columns:
            expected_entity = entity_map.get(column)
            for value in original_df[column].fillna("").astype(str):
                total += 1
                normalized = self._normalize_for_detection(column, value)
                results = detect_pii(normalized, self.analyzer)
                if any(result.entity_type == expected_entity for result in results):
                    detected += 1
        return detected / total if total else 0.0
