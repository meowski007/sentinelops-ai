import pytest

from app.services.remediation_service import RemediationService


def test_propose_remediation_success(db_session):
    service = RemediationService(db_session)
    req = service.propose_remediation(
        incident_id="INC-2026-001",
        proposed_action="rollback_deployment",
        reason_summary="Elevated 5xx rate following release v2.4.1",
        expected_impact="Restores gateway to stable v2.4.0",
        risk_level="HIGH",
        action_parameters={"service_id": "api-gateway", "target_version": "v2.4.0"},
    )
    assert req.id is not None
    assert req.approval_status == "PENDING_APPROVAL"
    assert req.execution_status == "PENDING"

def test_propose_unallowlisted_action_fails(db_session):
    service = RemediationService(db_session)
    with pytest.raises(ValueError, match="not in the approved remediation allowlist"):
        service.propose_remediation(
            incident_id="INC-2026-001",
            proposed_action="rm_rf_root_directory",  # Disallowed command
            reason_summary="Malicious or unallowlisted action",
            expected_impact="Severe",
            risk_level="HIGH",
        )

def test_execute_unapproved_remediation_fails(db_session):
    service = RemediationService(db_session)
    req = service.propose_remediation(
        incident_id="INC-2026-001",
        proposed_action="rollback_deployment",
        reason_summary="Need rollback",
        expected_impact="Restores gateway",
        risk_level="HIGH",
    )
    # Attempt execution while approval_status is still PENDING_APPROVAL
    with pytest.raises(PermissionError, match="approval status is 'PENDING_APPROVAL'"):
        service.execute_remediation(remediation_id=req.id, operator_id="operator@sentinelops.local")

def test_approve_and_execute_workflow(db_session):
    service = RemediationService(db_session)
    req = service.propose_remediation(
        incident_id="INC-2026-001",
        proposed_action="rollback_deployment",
        reason_summary="Rollback v2.4.1",
        expected_impact="Normalize error rates",
        risk_level="HIGH",
        action_parameters={"target_version": "v2.4.0"},
    )

    # Human approval
    approved_req = service.approve_remediation(
        remediation_id=req.id,
        approver_id="lead-operator@sentinelops.local",
        notes="Approved for emergency stabilization",
    )
    assert approved_req.approval_status == "APPROVED"
    assert approved_req.approver_id == "lead-operator@sentinelops.local"

    # Execution
    executed_req = service.execute_remediation(
        remediation_id=req.id,
        operator_id="operator@sentinelops.local",
    )
    assert executed_req.execution_status == "EXECUTED"
    assert executed_req.executed_at is not None
    assert "Simulated rollback" in executed_req.execution_result

    # Duplicate execution prevention
    with pytest.raises(ValueError, match="already been executed"):
        service.execute_remediation(
            remediation_id=req.id,
            operator_id="operator@sentinelops.local",
        )

def test_reject_remediation_workflow(db_session):
    service = RemediationService(db_session)
    req = service.propose_remediation(
        incident_id="INC-2026-002",
        proposed_action="drain_connection_pool",
        reason_summary="Drain pool",
        expected_impact="Restores connections",
        risk_level="MEDIUM",
    )

    rejected_req = service.reject_remediation(
        remediation_id=req.id,
        approver_id="lead@sentinelops.local",
        rejection_reason="Waiting for traffic dip before draining",
    )
    assert rejected_req.approval_status == "REJECTED"
    assert rejected_req.execution_status == "CANCELLED"

    # Cannot approve after rejection
    with pytest.raises(ValueError, match="Cannot approve already rejected"):
        service.approve_remediation(
            remediation_id=req.id,
            approver_id="lead@sentinelops.local",
        )
