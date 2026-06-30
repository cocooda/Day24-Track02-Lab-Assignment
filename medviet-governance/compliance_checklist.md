# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam.
  Production patient datasets, encrypted database snapshots, and object storage buckets are restricted to VN regions only. Cross-border replication is disabled for raw and restricted datasets.
- [x] Backup cũng phải ở trong lãnh thổ VN.
  Daily backups of production databases and weekly immutable snapshots are stored in a secondary VN datacenter with the same residency policy as production.
- [x] Log việc transfer data ra ngoài nếu có.
  Any export job must emit an audit log with requestor, approval ticket, dataset classification, destination system, destination country, and timestamp. Restricted datasets are denied if destination country is not `VN`.

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training.
  Consent is collected through the patient intake workflow before records are copied into the training-data pipeline. Records without consent are excluded from training exports.
- [x] Có mechanism để user rút consent (Right to Erasure).
  A consent-withdrawal workflow revokes downstream training eligibility, triggers deletion of linked derived records where required, and creates an erasure task for platform operations.
- [x] Lưu consent record với timestamp.
  Consent records store patient identifier, consent scope, collection method, versioned policy text, and an RFC 3339 timestamp for auditability.

## C. Breach Notification (72h)
- [x] Có incident response plan.
  Security incidents follow a written playbook with severity classification, evidence preservation, legal review, and communication owners.
- [x] Alert tự động khi phát hiện breach.
  API anomaly detection, access-log correlation, and secret-scanning alerts notify the security on-call channel and incident manager automatically.
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h.
  The incident checklist requires legal and DPO review, a regulator notification draft, and escalation milestones to ensure formal breach notice is sent within 72 hours when legally required.

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer.
  MedViet designates a DPO within the governance program to approve policies, review incidents, and oversee subject-right requests.
- [x] DPO có thể liên hệ tại: dpo@medviet.example.vn

## E. Technical Controls
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | Deterministic PII detection and anonymization pipeline before analytics/training export | ✅ Implemented | AI Platform Team |
| Access control | Casbin RBAC for API actions plus OPA policy for attribute-based governance decisions | ✅ Implemented | Platform Security |
| Encryption at rest and in transit | AES-256-GCM envelope encryption for sensitive columns, TLS 1.3 required for service traffic, KEK excluded from submission artifacts | ✅ Implemented | Infrastructure |
| Audit logging | API gateway request logs, consent audit records, export approval logs, and delete-operation trails retained in VN storage | ✅ Planned Control | Platform Security |
| Breach/anomaly detection | Secret scanning, API anomaly alerts, access-denial monitoring, and incident escalation workflow | ✅ Planned Control | Security Operations |
| Data localization | VN-only production and backup regions enforced through infrastructure policy | ✅ Planned Control | Infrastructure |
| Consent lifecycle | Consent capture, timestamped record storage, withdrawal workflow, and downstream suppression from training datasets | ✅ Planned Control | Product + Legal |
| Erasure / withdrawal | Subject-right request queue with deletion confirmation and downstream propagation status tracking | ✅ Planned Control | Privacy Operations |
| RBAC/ABAC mapping | Role policies for admin/ML engineer/data analyst/intern plus export-country deny logic | ✅ Implemented | Platform Security |

## F. Concrete Technical Solutions
- Audit logging: Every access to `/api/patients/raw`, `/api/patients/anonymized`, `/api/metrics/aggregated`, and delete operations should emit structured JSON logs containing actor, role, endpoint, action, request ID, timestamp, and authorization outcome. Logs are forwarded to a VN-resident SIEM with 180-day retention.
- Breach/anomaly detection: Add threshold alerts for abnormal access spikes, repeated 403/401 bursts, high-volume export attempts, and secret-scan hits in pull requests. Incidents open automatically in the security queue with severity hints.
- Data localization: Terraform or cloud policy must pin storage/database resources to VN regions and block creation of raw-patient replicas outside VN. Any exception requires DPO approval and documented compensating controls.
- Consent collection: The intake application should store consent records in a dedicated table with consent text version, capture channel, operator ID when applicable, and signature/evidence metadata.
- Consent withdrawal / right to erasure: A withdrawal event should mark the patient as excluded from future model-training jobs, queue deletion of cached derived datasets, and create a reconciliation report proving downstream propagation.
- Encryption at rest and in transit: Sensitive fields use envelope encryption with a locally stored KEK only for lab development. Production must move the KEK to HSM/KMS and enforce TLS 1.3 for all service-to-service and client API calls.
- Data minimization: Training endpoints expose only anonymized or aggregated outputs. Raw identifiers are blocked from ML-engineer, analyst, and intern roles.
