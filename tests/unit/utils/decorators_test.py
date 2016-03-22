# -*- coding: utf-8 -*-
'''
    :codeauthor: :email:`Bo Maryniuk (bo@suse.de)`
    unit.utils.decorators_test
'''

# Import Pytohn libs
from __future__ import absolute_import

# Import Salt Testing libs
from salttesting import TestCase
from salttesting.helpers import ensure_in_syspath
from salt.utils import decorators
from salt.version import SaltStackVersion
from salt.exceptions import CommandExecutionError

ensure_in_syspath('../../')


class DummyLogger(object):
    '''
    Dummy logger accepts everything and simply logs
    '''
    def __init__(self, messages):
        self._messages = messages

    def __getattr__(self, item):
        return self._log

    def _log(self, msg):
        self._messages.append(msg)


class DecoratorsTest(TestCase):
    '''
    Testing decorators.
    '''
    def old_function(self):
        return "old"

    def new_function(self):
        return "new"

    def _mk_version(self, name):
        '''
        Make a version

        :return:
        '''
        return name, SaltStackVersion.from_name(name)

    def setUp(self):
        '''
        Setup a test
        :return:
        '''
        self.globs = {
            '__opts__': {},
            'old_function': self.old_function,
            'new_function': self.new_function,
        }
        self.messages = list()
        decorators.log = DummyLogger(self.messages)

    def test_is_deprecated_lo_hi_version(self):
        '''
        Use of is_deprecated will result to the exception,
        if the expiration version is lower than the current version.
        A successor function is not pointed.

        :return:
        '''
        depr = decorators.is_deprecated(self.globs, "Helium")
        depr._curr_version = self._mk_version("Beryllium")[1]
        with self.assertRaises(CommandExecutionError):
            depr(self.old_function)()
        self.assertEqual(self.messages,
                         ['The lifetime of the function "old_function" expired.'])

    def test_is_deprecated_hi_lo_version(self):
        '''
        Use of is_deprecated will result to the log message,
        if the expiration version is higher than the current version.

        :return:
        '''
        depr = decorators.is_deprecated(self.globs, "Beryllium")
        depr._curr_version = self._mk_version("Helium")[1]
        depr(self.old_function)()

        self.assertEqual(self.messages,
                         ['The function "old_function" is deprecated '
                          'and will expire in version "Beryllium".'])

    def with_deprecated_test(self):
        pass

if __name__ == '__main__':
    from integration import run_tests
    run_tests(DecoratorsTest, needs_daemon=False)
