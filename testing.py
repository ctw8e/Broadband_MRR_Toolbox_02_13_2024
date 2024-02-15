"""
Author: Channing West
Changelog: 10/22/2022
"""

import gc
import cProfile
import pstats
import io
import tracemalloc


def profile_func(func):
    """ Profile execution time and print sorted stats to console. Function decorator. """
    def decorator_func(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        val = func(*args, **kwargs)
        pr.disable()
        s = io.StringIO()
        sortby = 'cumulative'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        return val
    return decorator_func


def collect_garbage(func):
    """ Clear memory. Function decorator """
    def decorator_func(*args, **kwargs):
        gc.collect()
        val = func(*args, **kwargs)
        return val
    return decorator_func


def memory_allocation(func):
    """ Compare memory allocation before and after function executes. Function decorator. """
    def decorator_func(*args, **kwargs):
        tracemalloc.start()
        s1 = tracemalloc.take_snapshot()
        val = func(*args, **kwargs)
        s2 = tracemalloc.take_snapshot()
        top_stats = s2.compare_to(s1, 'lineno')
        print("[ Top 10 differences ]")
        for stat in top_stats[:10]:
            print(stat)
        return val
    return decorator_func
