"""
Incident Detection Rules and Statistical Thresholds
Provides explainable rule definitions and time-window metric computations.
"""
from typing import Dict, List

import numpy as np


class DetectionRule:
    def __init__(
        self,
        rule_id: str,
        metric_name: str,
        threshold: float,
        operator: str,  # "GT" (greater than), "LT" (less than)
        severity: str,
        description: str,
    ):
        self.rule_id = rule_id
        self.metric_name = metric_name
        self.threshold = threshold
        self.operator = operator
        self.severity = severity
        self.description = description

    def evaluate(self, value: float) -> bool:
        if self.operator == "GT":
            return value > self.threshold
        elif self.operator == "LT":
            return value < self.threshold
        return False

# Standard Enterprise IT Detection Rules
DEFAULT_DETECTION_RULES = [
    DetectionRule(
        rule_id="ERROR_RATE_THRESHOLD_EXCEEDED",
        metric_name="error_rate",
        threshold=5.0,
        operator="GT",
        severity="CRITICAL",
        description="HTTP error rate exceeded 5.0% threshold (indicates active customer-facing outage).",
    ),
    DetectionRule(
        rule_id="LATENCY_P95_THRESHOLD_EXCEEDED",
        metric_name="latency_p95",
        threshold=2000.0,
        operator="GT",
        severity="HIGH",
        description="p95 round-trip latency exceeded 2000ms threshold (indicates bottleneck or pool exhaustion).",
    ),
    DetectionRule(
        rule_id="QUEUE_DEPTH_THRESHOLD_EXCEEDED",
        metric_name="queue_depth",
        threshold=1000.0,
        operator="GT",
        severity="HIGH",
        description="Asynchronous worker backlog exceeded 1,000 tasks (indicates consumer starvation or crash loop).",
    ),
    DetectionRule(
        rule_id="AUTH_FAILURE_RATE_EXCEEDED",
        metric_name="auth_failure_rate",
        threshold=10.0,
        operator="GT",
        severity="CRITICAL",
        description="Authentication rejections exceeded 10.0% threshold (indicates expired certificate or identity outage).",
    ),
]

def calculate_time_window_stats(values: List[float]) -> Dict[str, float]:
    """Computes median (p50), 95th percentile (p95), min, max, and mean over a window."""
    if not values:
        return {"mean": 0.0, "p50": 0.0, "p95": 0.0, "min": 0.0, "max": 0.0}
    arr = np.array(values, dtype=np.float64)
    return {
        "mean": round(float(np.mean(arr)), 2),
        "p50": round(float(np.percentile(arr, 50)), 2),
        "p95": round(float(np.percentile(arr, 95)), 2),
        "min": round(float(np.min(arr)), 2),
        "max": round(float(np.max(arr)), 2),
    }
