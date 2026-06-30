from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO_ROOT / "medviet-governance" / "policies" / "medviet-data-policy.yaml"
REPORT_PATH = REPO_ROOT / "medviet-governance" / "reports" / "agent_governance.md"


def test_agent_governance_policy_exists_with_required_rules():
    content = POLICY_PATH.read_text(encoding="utf-8")

    assert POLICY_PATH.exists()
    assert "default" in content.lower()
    assert "deny" in content.lower()
    assert "anonymized" in content.lower()
    assert "raw" in content.lower()
    assert "vn" in content.lower()
    assert "data_analyst" in content
    assert "aggregated" in content.lower()
    assert "delete" in content.lower()
    assert "human" in content.lower()


def test_agent_governance_report_documents_limitations_and_install():
    content = REPORT_PATH.read_text(encoding="utf-8")

    assert REPORT_PATH.exists()
    assert "AGT" in content
    assert "RBAC" in content
    assert "OPA" in content
    assert "installed" in content.lower() or "cài" in content.lower()
    assert "pip install" in content
