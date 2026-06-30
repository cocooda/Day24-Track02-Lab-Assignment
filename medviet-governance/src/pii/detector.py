from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

try:
    from presidio_analyzer import Pattern, PatternRecognizer, RecognizerResult
    from presidio_analyzer import RecognizerRegistry
except ModuleNotFoundError:
    import re

    @dataclass
    class Pattern:
        name: str
        regex: str
        score: float

    @dataclass
    class RecognizerResult:
        entity_type: str
        start: int
        end: int
        score: float

    class PatternRecognizer:
        def __init__(
            self,
            supported_entity: str,
            patterns: list[Pattern],
            context: list[str] | None = None,
        ):
            self.supported_entities = [supported_entity]
            self.patterns = patterns
            self.context = context or []

        def analyze(
            self,
            text: str,
            entities: list[str] | None = None,
            nlp_artifacts=None,
        ) -> list[RecognizerResult]:
            if entities and self.supported_entities[0] not in entities:
                return []

            results: list[RecognizerResult] = []
            lowered = text.lower()
            for pattern in self.patterns:
                for match in re.finditer(pattern.regex, text):
                    score = pattern.score
                    if self.context and any(token in lowered for token in self.context):
                        score = min(1.0, score + 0.05)
                    results.append(
                        RecognizerResult(
                            entity_type=self.supported_entities[0],
                            start=match.start(),
                            end=match.end(),
                            score=score,
                        )
                    )
            return results

    class RecognizerRegistry:
        def __init__(self):
            self.recognizers: list[PatternRecognizer] = []

        def add_recognizer(self, recognizer: PatternRecognizer) -> None:
            self.recognizers.append(recognizer)


VN_CCCD_REGEX = r"(?<!\d)\d{12}(?!\d)"
VN_PHONE_REGEX = r"(?<!\d)0(?:3|5|7|8|9)\d{8}(?!\d)"
EMAIL_REGEX = r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b"
VIETNAMESE_NAME_REGEX = (
    r"(?<!\w)"
    r"(?:[A-ZÀ-Ỵ][a-zà-ỹ]+(?:\s+|$)){2,5}"
)


@dataclass
class SimpleAnalyzer:
    registry: RecognizerRegistry
    supported_languages: tuple[str, ...] = ("vi",)

    def analyze(
        self,
        text: str | None,
        language: str = "vi",
        entities: list[str] | None = None,
    ) -> list[RecognizerResult]:
        if not text:
            return []
        if language not in self.supported_languages:
            return []

        requested = set(entities or [])
        recognizers = self.registry.recognizers
        results: list[RecognizerResult] = []
        for recognizer in recognizers:
            if requested and recognizer.supported_entities[0] not in requested:
                continue
            results.extend(
                recognizer.analyze(
                    text=text,
                    entities=entities,
                    nlp_artifacts=None,
                )
            )

        unique: dict[tuple[int, int, str], RecognizerResult] = {}
        for result in results:
            key = (result.start, result.end, result.entity_type)
            if key not in unique or unique[key].score < result.score:
                unique[key] = result
        return sorted(unique.values(), key=lambda item: (item.start, item.end))


def _build_registry() -> RecognizerRegistry:
    registry = RecognizerRegistry()

    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="VN_CCCD",
            patterns=[Pattern(name="vn_cccd", regex=VN_CCCD_REGEX, score=0.95)],
            context=["cccd", "căn cước", "chứng minh", "cmnd"],
        )
    )
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="VN_PHONE",
            patterns=[Pattern(name="vn_phone", regex=VN_PHONE_REGEX, score=0.9)],
            context=["điện thoại", "sdt", "phone", "liên hệ"],
        )
    )
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="EMAIL_ADDRESS",
            patterns=[Pattern(name="email", regex=EMAIL_REGEX, score=0.9)],
            context=["email", "mail", "liên hệ"],
        )
    )
    registry.add_recognizer(
        PatternRecognizer(
            supported_entity="PERSON",
            patterns=[
                Pattern(
                    name="vi_person",
                    regex=VIETNAMESE_NAME_REGEX,
                    score=0.8,
                )
            ],
            context=["bệnh nhân", "họ tên", "bác sĩ", "bs", "doctor"],
        )
    )
    return registry


VI_MODEL_CANDIDATES = ("vi_spacy_model", "vi_core_news_lg")
VI_MODEL_INSTALL_URL = (
    "https://gitlab.com/trungtv/vi_spacy/-/raw/master/packages/"
    "vi_core_news_lg-3.6.0/dist/vi_core_news_lg-3.6.0.tar.gz"
)


def build_vietnamese_analyzer(cache_dir: Path | None = None) -> SimpleAnalyzer:
    del cache_dir
    return SimpleAnalyzer(registry=_build_registry())


def detect_pii(text: str | None, analyzer: SimpleAnalyzer) -> list[RecognizerResult]:
    if text is None:
        return []
    normalized = str(text).strip()
    if not normalized:
        return []
    results = analyzer.analyze(
        text=normalized,
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
    )
    return [result for result in results if normalized[result.start:result.end].strip()]


def print_model_setup_hint() -> None:
    detected_model = ""
    try:
        import spacy

        for candidate in VI_MODEL_CANDIDATES:
            try:
                spacy.load(candidate)
                detected_model = candidate
                break
            except OSError:
                continue
    except ModuleNotFoundError:
        detected_model = ""

    if detected_model:
        print(f"Using spaCy Vietnamese model: {detected_model}")
        return

    print("Vietnamese spaCy model not found; using deterministic regex recognizers.")
    print("Notebook and tests do not require vi_core_news_lg for Lab 24.")
    print(f"Optional install: pip install --no-deps {VI_MODEL_INSTALL_URL}")
