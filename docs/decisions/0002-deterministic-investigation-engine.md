# ADR 0002: Deterministic Grounded Investigation Engine as Default

## Context
Generative LLMs frequently hallucinate facts, make up plausible-sounding log lines, or cite nonexistent documentation. In high-stakes enterprise IT operations and student internship evaluations, fabricated evidence is completely unacceptable.

## Decision
We make `LOCAL_DETERMINISTIC` the primary default investigation mode.
- The assistant retrieves real facts via allowlisted tools.
- Findings and hypotheses are generated through deterministic correlation rules.
- Every citation is bound to a verified source ID (`LOG-2`, `DEPLOY-1`, `METRIC-latency_p95`).
- External LLM generation is supported as an optional plugin behind a validated Pydantic schema, falling back to the deterministic engine on failure.

## Consequences
- **Positive**: 100% reproducible diagnoses with zero fabricated facts.
- **Positive**: No paid API keys or cloud dependencies needed to run the project.
- **Negative**: Rule-based synthesis is constrained to modeled scenarios and does not synthesize novel cross-domain prose like a frontier model.
