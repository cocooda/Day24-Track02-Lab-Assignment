# Lab 24 MedViet Governance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete all Lab 24 governance and security requirements with passing tests, generated reports, and a safe submission package.

**Architecture:** Build the solution around a deterministic local-first data governance pipeline: synthetic data generation, regex-backed PII detection with Presidio integration, anonymization and validation utilities, RBAC and OPA access control, and envelope encryption for sensitive fields. Keep Windows compatibility explicit for security tooling and CLI verification.

**Tech Stack:** Python, pandas, Faker, Presidio, FastAPI, Casbin, cryptography, Great Expectations, pytest, OPA, Bandit, TruffleHog

---

### Task 1: Scaffold and dataset foundation
- [ ] Normalize folders, package markers, `.gitignore`, and dataset documentation.
- [ ] Generate `data/raw/patients_raw.csv` with 200 deterministic synthetic records.

### Task 2: PII detection and anonymization
- [ ] Finish `tests/test_pii.py` with detection, detection-rate, preservation, and output-file assertions.
- [ ] Implement `src/pii/detector.py` with regex recognizers and Windows-safe fallbacks.
- [ ] Implement `src/pii/anonymizer.py` with replace, mask, hash, and dataframe anonymization.
- [ ] Run `pytest tests/test_pii.py -v --tb=short` until green.

### Task 3: RBAC API
- [ ] Add RBAC API tests for token handling and role restrictions.
- [ ] Implement Casbin policy/model integration and FastAPI endpoints.
- [ ] Run `pytest tests/test_rbac_api.py -v --tb=short` until green.

### Task 4: Encryption and data quality
- [ ] Add encryption and validation tests.
- [ ] Implement AES-256-GCM envelope encryption and anonymized-data validation.
- [ ] Run targeted tests until green.

### Task 5: Policy, compliance, audit, and packaging
- [ ] Finalize OPA policy and examples.
- [ ] Complete compliance checklist with concrete controls.
- [ ] Generate security tooling artifacts and document any Windows-specific limitations.
- [ ] Run full test suite, verify outputs, and create the submission zip.
