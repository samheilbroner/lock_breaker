from lock_breaker.string import levenshtein_distance


def test_levenstein_distance():
    word1 = 'a' * 200
    word2 = 'a' * 198 + 'b'
    assert levenshtein_distance(word1, word2) > 0