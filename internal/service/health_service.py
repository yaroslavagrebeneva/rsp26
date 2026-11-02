from datetime import datetime, timezone


def get_health_info(start_time: datetime) -> int:
    current_time = datetime.now(timezone.utc)
    uptime_seconds = current_time - start_time
    return int(uptime_seconds.total_seconds())
