# -*- coding: utf-8 -*-

from random import SystemRandom

def random_token(length, byte_filter):
    allowed_bytes = ''.join(c for c in map(chr, range(128)) if byte_filter(c))
    random = SystemRandom()
    return ''.join([random.choice(allowed_bytes) for _ in range(length)])

def alpha_numeric(length):
    return random_token(length, str.isalnum)

def lower_case(length):
    return random_token(length, str.islower)
