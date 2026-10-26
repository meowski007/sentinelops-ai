from app.monitoring.detector import AnomalyDetector
from app.monitoring.rules import (
    DetectionRule,
    calculate_time_window_stats,
)


def test_calculate_time_window_stats():
    values = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
    stats = calculate_time_window_stats(values)
    assert stats["min"] == 10.0
    assert stats["max"] == 100.0
    assert stats["p50"] == 55.0
    assert stats["p95"] > 90.0

def test_detection_rule_evaluation():
    rule = DetectionRule(
        rule_id="TEST_RULE",
        metric_name="error_rate",
        threshold=5.0,
        operator="GT",
        severity="CRITICAL",
        description="Test rule",
    )
    assert rule.evaluate(6.2) is True
    assert rule.evaluate(4.9) is False
    assert rule.evaluate(5.0) is False

def test_anomaly_detector_scan_telemetry(db_session):
    detector = AnomalyDetector()
    violations = detector.scan_service_telemetry(db_session, service_id="api-gateway")
    assert len(violations) > 0
    rule_ids = [v["rule_id"] for v in violations]
    assert "ERROR_RATE_THRESHOLD_EXCEEDED" in rule_ids

def test_anomaly_detector_healthy_service(db_session):
    detector = AnomalyDetector()
    violations = detector.scan_service_telemetry(db_session, service_id="notification-service")
    assert len(violations) == 0
