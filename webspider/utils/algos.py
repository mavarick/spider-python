"""
algorithms
"""
from random import choice
from random import random

def random_select(items):
    '''select random one from items'''
    if not items:
        return None
    return choice(items)

def wheel_select(items, weights):
    """select item from items depend on their weights"""
    sum_weight = sum(weights)
    select_index = random() * sum_weight
    for idx, weight in enumerate(weights):
        if weight < select_index:
            select_index = select_index - weight
        else:
            break
    return items[idx]

def _test_wheel_select():
    items = [1,2,3,4,5]
    weights = [1,2,3,4,5]
    for i in range(10):
        print wheel_select(items, weights)

def avg(lst):
    """ compute average of one number list|tuple
    """
    return sum(lst)*1.0/len(lst)

if __name__ == '__main__':
    _test_wheel_select()
    

