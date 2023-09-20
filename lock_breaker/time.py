from datetime import datetime, timezone

from lock_breaker import MAX_MINUTES_TO_COMPLETE


def within_time_limit(current_time: str):
    post_time = datetime.now(timezone.utc)
    get_time = datetime.fromisoformat(current_time).astimezone(timezone.utc)
    difference = (post_time - get_time).seconds / 60.0
    return difference <= MAX_MINUTES_TO_COMPLETE
