from datetime import datetime
from typing import List
from src.metrics.schemas import MetricDataPoint


def downsample_metrics(data_points: List[MetricDataPoint], max_points: int = 200) -> List[MetricDataPoint]:
    """
    Simple step downsampling to prevent flooding charts with 10,000+ raw points.
    """
    if len(data_points) <= max_points:
        return data_points

    step = len(data_points) / max_points
    result = []
    for i in range(max_points):
        idx = int(i * step)
        if idx < len(data_points):
            result.append(data_points[idx])
    return result
