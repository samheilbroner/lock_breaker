from lock_breaker.string import levenshtein_distance
from lock_breaker.time import within_time_limit


def input_is_valid(copied_text, text, current_time):
    return levenshtein_distance(copied_text, text) < 20 and \
           within_time_limit(current_time)