from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class MetricSampleOut(BaseModel):
    id: int
    service_id: str
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    model_config = ConfigDict(from_attributes=True)

class MetricSummary(BaseModel):
    metric_name: str
    current_value: float
    unit: str
    p50: float
    p95: float
    min_value: float
    max_value: float
    threshold_violation: bool
    trigger_rule: Optional[str] = None

class ServiceMetricsOverview(BaseModel):
    service_id: str
    service_name: str
    status: str
    error_rate: float
    latency_p95_ms: float
    cpu_percent: float
    request_volume: int
    queue_depth: Optional[int] = None
    samples: List[MetricSampleOut] = []

class MetricsOverviewResponse(BaseModel):
    timestamp: datetime
    services: List[ServiceMetricsOverview]
    active_incidents_count: int
    critical_count: int
