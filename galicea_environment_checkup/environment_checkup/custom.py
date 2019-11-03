# -*- coding: utf-8 -*-

import collections

from .core import Check

custom_checks_per_module = collections.defaultdict(list)

class CustomCheck(Check):
    def __init__(self, module, func):
        super(CustomCheck, self).__init__(module)
        self.func = func

    def _run(self, env):
        return self.func(env)

def custom_check(func):
    try:
        module = func.__module__.split('.')[2]
    except IndexError:
        module = ''

    custom_checks_per_module[module].append(
        CustomCheck(module=module, func=func)
    )

    return func

def get_checks_for_module(module_name):
    return custom_checks_per_module[module_name]
