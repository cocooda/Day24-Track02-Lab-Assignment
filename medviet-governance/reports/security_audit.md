# Security Audit Report — Lab 24

## Working Directory
Security audit commands were run from:
`C:\Users\Admin\Github\VinLab\Day24-Track02-Lab-Assignment\medviet-governance`

## Git-Secrets
- Installed: yes
- Hook installed to `.git/hooks/pre-commit`: yes
- Patterns configured:
  - VN CCCD
  - password assignment
  - secret_key assignment
  - AWS patterns
- Verification command used:
  - do not use `git secrets --help`
  - used direct path and scan commands instead:
    - `C:\Program Files\Git\bin\bash.exe -lc '"$HOME/.git-secrets/git-secrets" --scan'`
    - `C:\Program Files\Git\bin\bash.exe -lc '"$HOME/.git-secrets/git-secrets" --scan test_secret.py'`
    - `C:\Program Files\Git\bin\bash.exe -lc '"$HOME/.git-secrets/git-secrets" --pre_commit_hook --'`
- Fake credential test:
  - detected/blocked: yes
  - report files:
    - `reports/git_secrets_scan_test.txt`
    - `reports/git_secrets_hook_test.txt`
- Note: `git secrets --help` may fail on this Windows machine because Git cannot find the HTML documentation file. This does not affect scanning or hook execution.
- Additional note: a repository-wide `--scan` also flagged sample `CCCD` strings in the test suite, which are expected lab fixtures rather than leaked credentials.

## Bandit
- Command:
  `bandit -r src/ -f json -o reports/bandit_report.json`
- Result:
  - findings count: 0
  - status: passed

## Pip-Audit
- Command:
  `pip-audit --desc on > reports/pip_audit.txt`
- Result:
  - vulnerability count: 0
  - resolved or documented mitigation: resolved by upgrading the environment and requirements floor to `cryptography>=48.0.1` and `setuptools>=78.1.1`, then rerunning `pip-audit`

## TruffleHog Git History Scan
- Command:
  `docker run --rm -v "${PWD}:/pwd" trufflesecurity/trufflehog:latest git file:///pwd --only-verified > reports/trufflehog_report.txt`
- Result:
  - finished scanning: yes
  - verified secrets: 0
  - unverified secrets: 0
  - chunks/bytes: `chunks: 40`, `bytes: 109715`
- Note: the report file was regenerated with full stream capture so the exact Docker output is preserved in `reports/trufflehog_report.txt`.

## TruffleHog Filesystem Scan
- Command:
  `docker run --rm -v "${PWD}:/pwd" trufflesecurity/trufflehog:latest filesystem /pwd --only-verified > reports/trufflehog_filesystem_report.txt`
- Result:
  - finished scanning: yes
  - verified secrets: 0
  - unverified secrets: 0
  - chunks/bytes: `chunks: 54573`, `bytes: 493688002`
- Note: the filesystem scan traversed `.venv/` and logged Brotli decode errors for some compiled `.pyc` files, but it still completed and reported zero verified and unverified secrets.

## Final Safety Checks
- `data/raw/` excluded from submission zip: yes
- `.vault_key` excluded: yes
- `test_secret.py` removed: yes
- no real credentials included: yes
