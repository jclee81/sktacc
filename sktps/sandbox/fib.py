# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


def run(raw_data):
    message = raw_data[0]
    worker_id = raw_data[1]
    iteration_id = int(raw_data[2])
    return slow_fib(iteration_id)


def slow_fib(n):
    if n <= 1:
        return 1
    else:
        return slow_fib(n-1) + slow_fib(n-2)
