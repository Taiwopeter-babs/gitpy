# class
# def naive_grouper(inputs, n):
#     # num_groups = len(inputs) // n
#     # return [tuple(inputs[i * n : (i + 1) * n]) for i in range(num_groups)]
#     iters = [iter(inputs)] * n
#     return zip(*iters)


# for _ in naive_grouper(range(100000000), 10):
#     pass

import itertools
import operator
from typing import Callable, Iterable


# def my_takewhile(predicate: Callable, iterable: Iterable):
#     for x in iterable:
#         if predicate(x):
#             yield x
#         else:
#             break


# pred = lambda x: x < 5

# res = my_takewhile(pred, [1, 4, 5, 6])
# print(next(res))
# print(next(res))
# print(next(res))
# print(next(res))

ex = """tree d54f3328ed99b424f03102d07c0c98587166d076
parent c74b813a9ec88203a5d7c9ac307956f70e848688

most newest commit commit
hello
"""
iters_ex = iter(ex.splitlines())

# print([line for line in itertools.takewhile(operator.truth, iters_ex)])


for line in itertools.takewhile(operator.truth, iters_ex):
    print(line)
    key, value = line.split(" ", 1)
    assert key in ["tree", "parent"], "Unknown field, {}".format(key)

    if key == "tree":
        tree = value
    elif key == "parent":
        parent = value

print(next(iters_ex))
print(next(iters_ex))
# print("{}".format(iters_ex))
# message = "\n".join(iters_ex)
print("\n".join(["", "hello world"]))


# print(message)
