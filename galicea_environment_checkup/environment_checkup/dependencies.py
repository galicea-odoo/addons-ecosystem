# -*- coding: utf-8 -*-

import subprocess
import re
import cgi
from odoo.modules.module import load_information_from_description_file
from odoo.tools import which

from .core import Check, CheckSuccess, CheckWarning, CheckFail

class DependencyCheck(Check):
    dependency_type = None

    def __init__(self, module, dependency):
        super(DependencyCheck, self).__init__(module)
        self.dependency = dependency

    def _dependency_installed(self, env, name):
        raise NotImplementedError('Should be overriden by the subclass')

    def _installed_version(self, env, name):
        raise NotImplementedError('Should be overriden by the subclass')

    def _details(self):
        if 'install' in self.dependency:
            return 'Install command: <pre>{}</pre>'.format(self.dependency['install'])
        return None

    def __has_required_version(self, installed_version, version_expression):
        version_operator = '='
        version = self.dependency['version']
        if version[:1] in ['=', '~', '^']:
            version_operator = version[:1]
            version = version[1:]
        elif version[:2] in ['>=']:
            version_operator = version[:2]
            version = version[2:]

        # Py3 : map -> list(map
        #  https://stackoverflow.com/questions/33717314/attributeerror-map-obejct-has-no-attribute-index-python-3
        try:
            parsed_version = list(map(int, version.split('.')))
        except ValueError:
            raise CheckFail(
                'Invalid version expression',
                details = """
Allowed expressions are <pre>=x.y.z</pre>, <pre>&gt;=x.y.z</pre>, <pre>^x.z.y</pre>,
<pre>~x.y.z. Got <pre>{}</pre>""".format(cgi.escape(self.dependency['version']))
            )
        parsed_installed_version = list(map(int, installed_version.split('.'))) 

        parsed_version.extend(0 for _ in range(len(parsed_installed_version) - len(parsed_version)))
        parsed_installed_version.extend(0 for _ in range(len(parsed_version) - len(parsed_installed_version)))

        if version_operator == '^':
            if parsed_installed_version[:1] != parsed_version[:1]:
                return False
            version_operator = '>='
        elif version_operator == '~':
            if parsed_installed_version[:2] != parsed_version[:2]:
                return False
            version_operator = '>='

        if version_operator == '>=':
            return tuple(parsed_installed_version) >= tuple(parsed_version)
        elif version_operator == '=':
            return tuple(parsed_installed_version) == tuple(parsed_version)

        assert False

    def _run(self, env):
        name = self.dependency['name']
        if not self._dependency_installed(env, name):
            raise CheckFail(
                'Required {} - {} - is not installed.'.format(self.dependency_type, name),
                details=self._details()
            )
        if 'version' in self.dependency:
            version_expression = self.dependency['version']
            installed_version = self._installed_version(env, name)
            if not self.__has_required_version(installed_version, version_expression):
                raise CheckWarning(
                    'Required {} - {} - has version {}, but {} is needed.'.format(
                        self.dependency_type,
                        name,
                        installed_version,
                        version_expression
                    ),
                    details=self._details()
                )
        return CheckSuccess(
            'Required {} - {} - is installed.'.format(self.dependency_type, name),
            details=self._details()
        )

class InternalDependencyCheck(DependencyCheck):
    dependency_type = 'Odoo module'

    def _dependency_installed(self, env, name):
        return name in env.registry._init_modules

    def _installed_version(self, env, name):
        return env['ir.module.module'].sudo().search([('name', '=', name)]).latest_version

class PythonDependencyCheck(DependencyCheck):
    dependency_type = 'Python module'

    def _dependency_installed(self, env, name):
        try:
            __import__(name)
            return True
        except ImportError:
            return False

    def _installed_version(self, env, name):
        try:
            return __import__(name).__version__
        except AttributeError:
            raise CheckWarning(
                'Could not detect version of the Python module: {}.'.format(name),
                details=self._details()
            )

class ExternalDependencyCheck(DependencyCheck):
    dependency_type = 'system executable'

    def _dependency_installed(self, env, name):
        try:
            which(name)
            return True
        except IOError:
            return False

    def _installed_version(self, env, name):
        try:
            exe = which(name)
            out = str(subprocess.check_output([exe, '--version'])) # Py3 str()
            match = re.search('[\d.]+', out)
            if not match:
                raise CheckWarning(
                    'Unable to detect version for executable {}'.format(name),
                    details="Command {} --version returned <pre>{}</pre>".format(exe, out)
                )
            return match.group(0)
        except subprocess.CalledProcessError as e:
            raise CheckWarning(
                'Unable to detect version for executable {}: {}'.format(name, e),
                details=self._details()
            )

def get_checks_for_module(module_name):
    result = []

    manifest = load_information_from_description_file(module_name)
    manifest_checks = manifest.get('environment_checkup') or {}
    dependencies = manifest_checks.get('dependencies') or {}

    for dependency in dependencies.get('python') or []:
        result.append(PythonDependencyCheck(module_name, dependency))
    for dependency in dependencies.get('external') or []:
        result.append(ExternalDependencyCheck(module_name, dependency))
    for dependency in dependencies.get('internal') or []:
        result.append(InternalDependencyCheck(module_name, dependency))

    return result

def get_checks_for_module_recursive(module):
    class ModuleDFS(object):
        def __init__(self):
            self.visited_modules = set()
            self.checks = []

        def visit(self, module):
            if module.name in self.visited_modules:
                return
            self.visited_modules.add(module.name)
            self.checks += get_checks_for_module(module.name)
            for module_dependency in module.dependencies_id:
                if module_dependency.depend_id:
                    self.visit(module_dependency.depend_id)
            return self

    return ModuleDFS().visit(module).checks
