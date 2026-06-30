# Agent Governance

`medviet-data-policy.yaml` is a best-effort Agent Governance Toolkit policy for the notebook's Part 6 flow. It defaults to deny, allows reads of anonymized data, limits `data_analyst` to the `aggregated` dataset, blocks raw PII datasets, blocks exports outside `VN`, and requires human approval before any `delete` action.

This complements the existing controls rather than replacing them. Casbin RBAC in the API controls who can call application endpoints, OPA expresses broader policy decisions, and AGT adds pre-execution tool policy checks for agent actions in notebook or agent runtime scenarios.

AGT local status: not verified as installed in this workspace. The repository path `agent-governance-toolkit/` was not available here, so AGT execution was not run as part of this lab pass.

Install commands if needed:

```bash
pip install "agent-governance-toolkit[full]"
pip install -e "../agent-governance-toolkit/agent-governance-python/agent-governance-toolkit-core[full]"
```
