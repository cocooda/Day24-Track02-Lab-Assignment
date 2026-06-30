from functools import wraps
from pathlib import Path
from typing import Optional

from fastapi import Header, HTTPException

try:
    import casbin
except ModuleNotFoundError:
    casbin = None


MOCK_USERS = {
    "token-alice": {"username": "alice", "role": "admin"},
    "token-bob": {"username": "bob", "role": "ml_engineer"},
    "token-carol": {"username": "carol", "role": "data_analyst"},
    "token-dave": {"username": "dave", "role": "intern"},
}

ACCESS_DIR = Path(__file__).resolve().parent


class CsvPolicyEnforcer:
    def __init__(self, policy_path: Path):
        self.permissions: set[tuple[str, str, str]] = set()
        self.memberships: dict[str, set[str]] = {}
        self._load_policy(policy_path)

    def _load_policy(self, policy_path: Path) -> None:
        for raw_line in policy_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            parts = [item.strip() for item in line.split(",")]
            if parts[0] == "p" and len(parts) >= 4:
                self.permissions.add((parts[1], parts[2], parts[3]))
            elif parts[0] == "g" and len(parts) >= 3:
                self.memberships.setdefault(parts[1], set()).add(parts[2])

    def enforce(self, subject: str, resource: str, action: str) -> bool:
        if (subject, resource, action) in self.permissions:
            return True
        return any(
            (role, resource, action) in self.permissions
            for role in self.memberships.get(subject, set())
        )


enforcer = (
    casbin.Enforcer(str(ACCESS_DIR / "model.conf"), str(ACCESS_DIR / "policy.csv"))
    if casbin is not None
    else CsvPolicyEnforcer(ACCESS_DIR / "policy.csv")
)


def get_current_user(authorization: Optional[str] = Header(None)) -> dict:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ", 1)[1]
    user = MOCK_USERS.get(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


def require_permission(resource: str, action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            role = current_user["role"]
            username = current_user["username"]
            allowed = enforcer.enforce(username, resource, action) or enforcer.enforce(
                role, resource, action
            )
            if not allowed:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{role}' cannot '{action}' on '{resource}'",
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator
