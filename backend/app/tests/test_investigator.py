from app.agents.investigator import IncidentInvestigator
from app.agents.tools import InvestigationTools


def test_investigation_tools_read_only(db_session):
    tools = InvestigationTools(db_session)
    details = tools.get_incident_details("INC-2026-001")
    assert "error" not in details
    assert details["id"] == "INC-2026-001"
    assert details["affected_service_id"] == "api-gateway"

    metrics = tools.get_service_metrics("api-gateway", window_minutes=60)
    assert "metrics" in metrics

    deployments = tools.get_recent_deployments("api-gateway")
    assert len(deployments) > 0
    assert deployments[0]["version"] == "v2.4.1"

    logs = tools.search_logs(service_id="api-gateway", level="ERROR")
    assert len(logs) > 0
    assert "LOG-" in logs[0]["id"]

def test_investigation_execution_and_evidence_citations(db_session):
    tools = InvestigationTools(db_session)
    investigator = IncidentInvestigator(db_session, tools)

    report = investigator.investigate("INC-2026-001")
    assert report["incident_id"] == "INC-2026-001"
    assert "summary" in report
    assert "root_cause_hypothesis" in report
    assert report["confidence"] in ["HIGH", "MEDIUM", "LOW"]
    assert len(report["supporting_evidence"]) > 0

    # Ensure evidence citations resolve to valid source identifiers
    for cit in report["supporting_evidence"]:
        assert cit["source_type"] in ["DEPLOYMENT", "METRIC", "LOG", "RUNBOOK"]
        assert len(cit["source_id"]) > 0

    # Ensure recommended remediation action is populated
    assert report["suggested_remediation"] == "rollback_deployment"
    assert report["requires_approval"] is True
