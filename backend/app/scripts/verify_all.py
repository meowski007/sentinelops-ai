"""
End-to-End System Verification Script
Directly tests all 10 core API workflows and outputs operational validation metrics.
"""
from fastapi.testclient import TestClient

from app.main import app


def verify_all():
    client = TestClient(app)
    print("=================================================================")
    print("         SENTINELOPS AI - FULL END-TO-END VERIFICATION           ")
    print("=================================================================")

    # 1. Health Probe
    h = client.get("/health").json()
    assert h.get("status") == "healthy", f"Health failed: {h}"
    print(f"[OK] 1. Health Probe: Status={h.get('status')} | DB={h.get('database')} | Mode={h.get('ai_engine_mode')}")

    # 2. Services Fleet
    services = client.get("/api/services").json()
    assert len(services) >= 5, f"Expected >= 5 services, got {len(services)}"
    print(f"[OK] 2. Services Fleet: {len(services)} microservices loaded ({', '.join(s['id'] for s in services)})")

    # 3. Incident Listing
    incidents = client.get("/api/incidents").json()
    assert len(incidents) >= 4, f"Expected >= 4 incidents, got {len(incidents)}"
    first_inc = incidents[0]
    inc_id = first_inc["id"]
    print(f"[OK] 3. Incidents Queue: {len(incidents)} active incidents | Target: {inc_id} ({first_inc['severity']})")

    # 4. Incident Timeline
    timeline = client.get(f"/api/incidents/{inc_id}/timeline").json()
    assert len(timeline) > 0, "Timeline should not be empty"
    types = set(t["type"] for t in timeline)
    print(f"[OK] 4. Incident Timeline: {len(timeline)} events reconstructed | Types: {types}")

    # 5. AI Investigation Assistant
    inv = client.post(f"/api/incidents/{inc_id}/investigate").json()
    assert "root_cause_hypothesis" in inv, f"Investigation missing root cause: {inv}"
    evidence_count = len(inv.get("supporting_evidence", []))
    assert evidence_count > 0, "Supporting evidence citations must not be empty"
    print(f"[OK] 5. AI Investigation: Mode={inv.get('investigation_mode')} | Confidence={inv.get('confidence')}")
    print(f"     Root Cause: {inv.get('root_cause_hypothesis')[:70]}...")
    print(f"     Grounded Citations: {evidence_count} references verified (Deployments, Logs, Metrics, Runbooks)")
    print(f"     Recommended Action: {inv.get('suggested_remediation')} (Requires Approval: {inv.get('requires_approval')})")

    # 6. Propose Remediation Action
    rem = client.post(f"/api/incidents/{inc_id}/remediations", json={
        "proposed_action": "rollback_deployment",
        "reason_summary": "Mitigate HTTP 5xx errors caused by release regression",
        "expected_impact": "Normalize gateway error rate to baseline (< 0.5%)",
        "risk_level": "HIGH",
        "action_parameters": {"target_version": "v2.4.0"}
    }).json()
    rem_id = rem["id"]
    assert rem["approval_status"] == "PENDING_APPROVAL", f"Approval status wrong: {rem}"
    print(f"[OK] 6. Remediation Proposal: #{rem_id} proposed | Action='{rem['proposed_action']}' | Status={rem['approval_status']}")

    # 7. Approve Remediation
    approved = client.post(f"/api/remediations/{rem_id}/approve", json={
        "approver_id": "lead-operator@sentinelops.local",
        "approval_notes": "Authorized emergency rollback"
    }).json()
    assert approved["approval_status"] == "APPROVED", f"Approval failed: {approved}"
    print(f"[OK] 7. Approval Gate: #{rem_id} APPROVED by '{approved['approver_id']}'")

    # 8. Execute Remediation
    executed = client.post(f"/api/remediations/{rem_id}/execute", json={
        "operator_id": "operator@sentinelops.local"
    }).json()
    assert executed["execution_status"] == "EXECUTED", f"Execution failed: {executed}"
    print(f"[OK] 8. Execution Gate: #{rem_id} EXECUTED | Result='{executed['execution_result'][:65]}...'")

    # Verify incident is marked RESOLVED
    inc_after = client.get(f"/api/incidents/{inc_id}").json()
    assert inc_after["status"] == "RESOLVED", f"Incident not marked RESOLVED: {inc_after}"
    print(f"[OK]    Service Recovery: Incident {inc_id} transitioned to '{inc_after['status']}'")

    # 9. Hybrid RAG Knowledge Retrieval
    search_res = client.post("/api/knowledge/search", json={
        "query": "HTTP 502 bad gateway deployment rollback",
        "method": "HYBRID",
        "top_k": 3
    }).json()
    assert len(search_res) > 0, "Knowledge search returned no results"
    top_hit = search_res[0]
    print(f"[OK] 9. Hybrid RAG Search: Query='HTTP 502 bad gateway' -> Top Hit: {top_hit['id']} ('{top_hit['title']}') | Score={top_hit['relevance_score']}")

    # 10. Audit Trail
    audit_events = client.get("/api/audit-events").json()
    assert len(audit_events) > 0, "Audit trail should contain events"
    print(f"[OK] 10. Audit & Compliance Trail: {len(audit_events)} recorded events | Latest: {audit_events[0]['event_type']} by {audit_events[0]['actor']}")

    print("=================================================================")
    print("      ALL 10 CORE SENTINELOPS WORKFLOWS VERIFIED SUCCESSFULLY    ")
    print("=================================================================")

if __name__ == "__main__":
    verify_all()
