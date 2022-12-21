import pandas as pd

from lock_breaker import MAX_MINUTES_TO_COMPLETE


def within_time_limit(current_time: str):
    post_time = pd.Timestamp.now()
    get_time = pd.to_datetime(current_time)
    difference = (post_time - get_time).seconds / 60.
    return difference <= MAX_MINUTES_TO_COMPLETE