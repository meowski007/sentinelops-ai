# ADR 0003: Backend Human-in-the-Loop Remediation Gates

## Context
Automated remediation systems that can execute commands without human sign-off represent a catastrophic risk in production environments. Even a slight misdiagnosis could result in rolling back the wrong service or dropping active databases.

## Decision
We enforce strict backend authorization gates:
1. Proposed actions must belong to an explicit allowlist.
2. State changes are partitioned into risk classifications (`HIGH`, `MEDIUM`, `LOW`).
3. High and medium-risk actions require explicit human sign-off (`PENDING_APPROVAL` -> `APPROVED`).
4. The execution endpoint rejects unapproved requests with `403 Forbidden`.
5. An immutable audit event is recorded for every proposal, approval, rejection, and execution.

## Consequences
- **Positive**: Complete defense-in-depth preventing accidental or unauthorized infrastructure mutations.
- **Positive**: Provides full compliance and audit transparency.
- **Negative**: Adds a human interaction step to the resolution loop before execution.
