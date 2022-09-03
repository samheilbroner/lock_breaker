import pandas as pd


def within_time_limit(current_time: str):
    post_time = pd.Timestamp.now()
    get_time = pd.to_datetime(current_time)
    difference = (post_time - get_time).seconds / 60.
    return difference <= 15