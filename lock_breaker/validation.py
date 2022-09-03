import logging
import random

from lock_breaker.string import levenshtein_distance
from lock_breaker.time import within_time_limit


def input_is_valid(copied_text, text, current_time):
    pass_random_test = random.uniform(0, 1) < 0.5
    score = levenshtein_distance(copied_text, text)
    time_limit = within_time_limit(current_time)
    print(f'score = {score}, within time limit = {time_limit}')
    return (score < len(text)*0.1) and time_limit and pass_random_test