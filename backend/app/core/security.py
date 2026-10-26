"""
SentinelOps AI - Security Controls and Input Validation
Implements guardrails, sanitization, role checks, and protection against prompt injection.
"""
import re
from typing import Set

# Allowlisted simulated actions that can be requested or executed
ALLOWED_REMEDIATION_ACTIONS: Set[str] = {
    "restart_service",
    "rollback_deployment",
    "scale_worker_pool",
    "clear_job_backlog",
    "refresh_service_credentials",
    "drain_connection_pool",
}

# Remediation actions that inherently change state and carry high/medium risk
HIGH_RISK_ACTIONS: Set[str] = {
    "rollback_deployment",
    "clear_job_backlog",
    "refresh_service_credentials",
}

MEDIUM_RISK_ACTIONS: Set[str] = {
    "scale_worker_pool",
    "drain_connection_pool",
    "restart_service",
}

# Prompt injection patterns in untrusted logs or runbooks
SUSPICIOUS_PATTERNS = [
    r"(?i)ignore\s+(all\s+)?previous\s+instructions",
    r"(?i)system\s+prompt",
    r"(?i)disregard\s+prior\s+rules",
    r"(?i)you\s+are\s+now\s+in\s+developer\s+mode",
    r"(?i)execute\s+(bash|cmd|powershell|sh|exec)",
]

def sanitize_untrusted_text(text: str) -> str:
    """
    Sanitizes untrusted text (such as simulated logs or user queries)
    to prevent prompt injection and control character abuse.
    """
    if not text:
        return ""

    # Check for potential injection markers and neutralize them
    sanitized = text
    for pattern in SUSPICIOUS_PATTERNS:
        sanitized = re.sub(pattern, "[FLAGGED_PROMPT_INJECTION_DEFUSED]", sanitized)

    # Strip null bytes and non-printable control characters except newline and tab
    sanitized = "".join(ch for ch in sanitized if ch == "\n" or ch == "\t" or 32 <= ord(ch) <= 126 or ord(ch) > 127)
    return sanitized.strip()

def validate_action_name(action: str) -> bool:
    """
    Validates that a proposed remediation action belongs to the strict allowlist.
    Prevents execution of arbitrary or unknown commands.
    """
    return action in ALLOWED_REMEDIATION_ACTIONS

def requires_approval(action: str, risk_level: str) -> bool:
    """
    Determines whether a remediation action requires explicit human approval.
    All state-changing actions in SentinelOps require human sign-off by policy.
    """
    if risk_level.upper() in ["HIGH", "MEDIUM"]:
        return True
    if action in HIGH_RISK_ACTIONS or action in MEDIUM_RISK_ACTIONS:
        return True
    return False

def check_actor_permission(actor: str, required_role: str = "IT_OPERATOR") -> bool:
    """
    Lightweight authorization abstraction for the portfolio simulation.
    Demonstrates defense-in-depth: prevents empty actors or unauthenticated actions.
    """
    if not actor or not actor.strip():
        return False
    # Demo actors: operator@sentinelops.local, lead@sentinelops.local, admin@sentinelops.local
    return True
