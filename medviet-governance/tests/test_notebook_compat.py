import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LAB_ROOT = REPO_ROOT / "data-governance-lab"
PII_UTILS_PATH = LAB_ROOT / "pii_utils.py"


def _load_pii_utils_module():
    spec = importlib.util.spec_from_file_location("lab_pii_utils", PII_UTILS_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pii_utils_exposes_notebook_api():
    module = _load_pii_utils_module()

    assert hasattr(module, "build_vietnamese_analyzer")
    assert hasattr(module, "detect_pii")
    assert hasattr(module, "print_model_setup_hint")


def test_pii_utils_detects_required_entities_without_model_download():
    module = _load_pii_utils_module()
    analyzer = module.build_vietnamese_analyzer(cache_dir=LAB_ROOT)
    text = "Nguyen Van A, CCCD 012345678901, SDT 0912345678, email a@b.com"

    results = module.detect_pii(text, analyzer)
    entity_types = {result.entity_type for result in results}

    assert "VN_CCCD" in entity_types
    assert "VN_PHONE" in entity_types
    assert "EMAIL_ADDRESS" in entity_types
