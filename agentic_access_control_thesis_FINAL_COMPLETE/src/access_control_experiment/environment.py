from __future__ import annotations

from copy import deepcopy
from .models import Action, ActionType, Case


class SyntheticEnvironment:
    """Mutable copy of one synthetic access-control case."""

    def __init__(self, case: Case):
        self.case = case
        self.identity = deepcopy(case.identity)
        self.context = deepcopy(case.context)
        self.exceptions = deepcopy(case.exceptions)

    def snapshot(self) -> dict:
        return {
            "identity": deepcopy(self.identity),
            "context": deepcopy(self.context),
            "exceptions": deepcopy(self.exceptions),
        }

    def has_active_exception(self, policy_id: str) -> bool:
        return any(
            ex.get("policy_id") == policy_id and bool(ex.get("valid", False))
            for ex in self.exceptions
        )

    def apply(self, action: Action) -> None:
        if action.type == ActionType.NO_ACTION:
            return

        if action.type in {
            ActionType.REMOVE_TEMP_ACCESS,
            ActionType.REMOVE_PROJECT_ACCESS,
            ActionType.REMOVE_PRIVILEGED_ACCESS,
            ActionType.REMOVE_SOD_ROLE,
        }:
            if not action.target:
                raise ValueError(f"{action.type} requires a target role")
            roles = list(self.identity.get("roles", []))
            if action.target in roles:
                roles.remove(action.target)
            self.identity["roles"] = roles
            return

        if action.type == ActionType.DISABLE_ACCOUNT:
            self.identity["account_enabled"] = False
            return

        raise ValueError(f"Unsupported action: {action.type}")
