# -*- coding: utf-8 -*-

from . import custom, dependencies

def all_installed_checks(env):
    result = []
    installed_modules = env.registry._init_modules
    for module_name in installed_modules:
        result += custom.get_checks_for_module(module_name)
        result += dependencies.get_checks_for_module(module_name)
    return result

def display_data(env, checks):
    response = []
    for check in checks:
        result = check.run(env)
        response.append({
            'module': check.module,
            'message': result.message,
            'details': result.details,
            'result': result.result
        })

    return response
