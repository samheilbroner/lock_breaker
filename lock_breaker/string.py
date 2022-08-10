import random

import numpy

from lock_breaker import TEXT_LENGTH
from lock_breaker.keys import TEXT_GENERATION_KEY
from lock_breaker.password import random_digits_from_encryption_key


def levenshtein_distance(token1, token2):
    distances = numpy.zeros((len(token1) + 1, len(token2) + 1))

    for t1 in range(len(token1) + 1):
        distances[t1][0] = t1

    for t2 in range(len(token2) + 1):
        distances[0][t2] = t2

    for t1 in range(1, len(token1) + 1):
        for t2 in range(1, len(token2) + 1):
            if (token1[t1 - 1] == token2[t2 - 1]):
                distances[t1][t2] = distances[t1 - 1][t2 - 1]
            else:
                a = distances[t1][t2 - 1]
                b = distances[t1 - 1][t2]
                c = distances[t1 - 1][t2 - 1]

                if (a <= b and a <= c):
                    distances[t1][t2] = a + 1
                elif (b <= a and b <= c):
                    distances[t1][t2] = b + 1
                else:
                    distances[t1][t2] = c + 1

    return distances[len(token1)][len(token2)]


def random_string(length):
    answer = ''
    for _ in range(length):
        index = random.randint(0, 25)
        answer += list('abcdefghijklmnopqrstuvwxyz')[index]
    return answer


def text_to_copy(current_time: str) -> str:
    hsh = int(random_digits_from_encryption_key(current_time, TEXT_GENERATION_KEY,
                                                password_length=8))
    random.seed(hsh)
    return random_string(TEXT_LENGTH)


def add_returns_to_text(text: str):
    answer = ''
    for i, char in enumerate(text):
        answer += char
        if (i + 1) % 50 == 0:
            answer += '\n'
    return answer