# -*- coding: utf-8 -*-

import logging
_logger = logging.getLogger(__name__)

class CheckResult(object):
    SUCCESS = 'success'
    WARNING = 'warning'
    FAIL = 'fail'

    def __init__(self, result, message, details = None):
        super(CheckResult, self).__init__()

        self.result = result
        self.message = message
        self.details = details

class CheckSuccess(CheckResult):
    def __init__(self, message, **kwargs):
        super(CheckSuccess, self).__init__(CheckResult.SUCCESS, message, **kwargs)

class CheckIssue(CheckResult, Exception):
    def __init__(self, result, message, **kwargs):
        Exception.__init__(self, message)
        CheckResult.__init__(self, result, message, **kwargs)

class CheckFail(CheckIssue):
    def __init__(self, message, **kwargs):
        super(CheckFail, self).__init__(CheckResult.FAIL, message, **kwargs)

class CheckWarning(CheckIssue):
    def __init__(self, message, **kwargs):
        super(CheckWarning, self).__init__(CheckResult.WARNING, message, **kwargs)

class Check(object):
    def __init__(self, module):
        self.module = module

    def run(self, env):
        try:
            return self._run(env)
        except CheckIssue as issue:
            return issue
        except Exception as ex:
            _logger.exception(ex)
            return CheckFail('Check failed when processing: {}'.format(ex))

    def _run(self, env):
        raise NotImplementedError('Should be overriden by the subclass')
