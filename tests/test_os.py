"""
Partial backport of Python 3.5's Lib/test/test_os.py.

Backport modifications are marked with "XXX backport".
"""
from __future__ import unicode_literals

from backports import os

import sys
import unittest
import warnings

from backports.test import support

# XXX backport: unicode on Python 2
_str = unicode if sys.version_info < (3,) else str


import mapping_tests

class EnvironTests(mapping_tests.BasicTestMappingProtocol):
    """check that os.environ object conform to mapping protocol"""
    type2test = None

    def setUp(self):
        self.__save = dict(os.environ)
        if os.supports_bytes_environ:
            self.__saveb = dict(os.environb)
        for key, value in self._reference().items():
            os.environ[key] = value

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.__save)
        if os.supports_bytes_environ:
            os.environb.clear()
            os.environb.update(self.__saveb)

    def _reference(self):
        return {"KEY1":"VALUE1", "KEY2":"VALUE2", "KEY3":"VALUE3"}

    def _empty_mapping(self):
        os.environ.clear()
        return os.environ

    # Bug 1110478
    @unittest.skipUnless(os.path.exists('/bin/sh'), 'requires /bin/sh')
    def test_update2(self):
        os.environ.clear()

        # XXX backport: os.environ.update(HELLO="World")
        os.environ.update(**{'HELLO': "World"})

        with os.popen("/bin/sh -c 'echo $HELLO'") as popen:
            value = popen.read().strip()
            self.assertEqual(value, "World")

    @unittest.skipUnless(os.path.exists('/bin/sh'), 'requires /bin/sh')
    def test_os_popen_iter(self):
        with os.popen(
            "/bin/sh -c 'echo \"line1\nline2\nline3\"'") as popen:
            it = iter(popen)
            self.assertEqual(next(it), "line1\n")
            self.assertEqual(next(it), "line2\n")
            self.assertEqual(next(it), "line3\n")
            self.assertRaises(StopIteration, next, it)

    # Verify environ keys and values from the OS are of the
    # correct str type.
    def test_keyvalue_types(self):
        for key, val in os.environ.items():
            self.assertEqual(type(key), _str)
            self.assertEqual(type(val), _str)

    def test_items(self):
        for key, value in self._reference().items():
            self.assertEqual(os.environ.get(key), value)

    # Issue 7310
    def test___repr__(self):
        """Check that the repr() of os.environ looks like environ({...})."""
        env = os.environ
        self.assertEqual(repr(env), 'environ({{{}}})'.format(', '.join(
            '{!r}: {!r}'.format(key, value)
            for key, value in env.items())))

    def test_get_exec_path(self):
        defpath_list = os.defpath.split(os.pathsep)
        test_path = ['/monty', '/python', '', '/flying/circus']
        test_env = {'PATH': os.pathsep.join(test_path)}

        saved_environ = os.environ
        try:
            os.environ = dict(test_env)
            # Test that defaulting to os.environ works.
            self.assertSequenceEqual(test_path, os.get_exec_path())
            self.assertSequenceEqual(test_path, os.get_exec_path(env=None))
        finally:
            os.environ = saved_environ

        # No PATH environment variable
        self.assertSequenceEqual(defpath_list, os.get_exec_path({}))
        # Empty PATH environment variable
        self.assertSequenceEqual(('',), os.get_exec_path({'PATH':''}))
        # Supplied PATH environment variable
        self.assertSequenceEqual(test_path, os.get_exec_path(test_env))

        if os.supports_bytes_environ:

            # XXX backport: Python 2 folds text and binary to the same key,
            # so the following is not possible.
            if (3,) <= sys.version_info:
                # env cannot contain 'PATH' and b'PATH' keys
                try:
                    # ignore BytesWarning warning
                    with warnings.catch_warnings(record=True):
                        mixed_env = {'PATH': '1', b'PATH': b'2'}
                except BytesWarning:
                    # mixed_env cannot be created with python -bb
                    pass
                else:
                    self.assertRaises(ValueError, os.get_exec_path, mixed_env)

            # bytes key and/or value
            self.assertSequenceEqual(os.get_exec_path({b'PATH': b'abc'}),
                ['abc'])
            self.assertSequenceEqual(os.get_exec_path({b'PATH': 'abc'}),
                ['abc'])
            self.assertSequenceEqual(os.get_exec_path({'PATH': b'abc'}),
                ['abc'])

    @unittest.skipUnless(os.supports_bytes_environ,
                         "os.environb required for this test.")
    def test_environb(self):
        # os.environ -> os.environb
        value = 'euro\u20ac'
        try:
            value_bytes = value.encode(sys.getfilesystemencoding(),
                                       'surrogateescape')
        except UnicodeEncodeError:
            msg = "U+20AC character is not encodable to %s" % (
                sys.getfilesystemencoding(),)
            self.skipTest(msg)
        os.environ['unicode'] = value
        self.assertEqual(os.environ['unicode'], value)
        self.assertEqual(os.environb[b'unicode'], value_bytes)

        # os.environb -> os.environ
        value = b'\xff'
        os.environb[b'bytes'] = value
        self.assertEqual(os.environb[b'bytes'], value)
        value_str = value.decode(sys.getfilesystemencoding(), 'surrogateescape')
        self.assertEqual(os.environ['bytes'], value_str)

    # On FreeBSD < 7 and OS X < 10.6, unsetenv() doesn't return a value (issue
    # #13415).
    @support.requires_freebsd_version(7)
    @support.requires_mac_ver(10, 6)
    def test_unset_error(self):
        if sys.platform == "win32":
            # an environment variable is limited to 32,767 characters
            key = 'x' * 50000
            self.assertRaises(ValueError, os.environ.__delitem__, key)
        else:
            # "=" is not allowed in a variable name
            key = 'key='
            self.assertRaises(OSError, os.environ.__delitem__, key)

    def test_key_type(self):
        missing = 'missingkey'
        self.assertNotIn(missing, os.environ)

        with self.assertRaises(KeyError) as cm:
            os.environ[missing]
        self.assertIs(cm.exception.args[0], missing)
        # XXX backport: Not applicable in Python 2
        # self.assertTrue(cm.exception.__suppress_context__)

        with self.assertRaises(KeyError) as cm:
            del os.environ[missing]
        self.assertIs(cm.exception.args[0], missing)
        # XXX backport: Not applicable in Python 2
        # self.assertTrue(cm.exception.__suppress_context__)

class FSEncodingTests(unittest.TestCase):
    def test_nop(self):
        self.assertEqual(os.fsencode(b'abc\xff'), b'abc\xff')
        self.assertEqual(os.fsdecode('abc\u0141'), 'abc\u0141')

    def test_identity(self):
        # assert fsdecode(fsencode(x)) == x
        for fn in ('unicode\u0141', 'latin\xe9', 'ascii'):
            try:
                bytesfn = os.fsencode(fn)
            except UnicodeEncodeError:
                continue

            # XXX backport: Ignore bug in future.utils.surrogateescape.replace_surrogate_encode()
            # by treating the below NameError like the above UnicodeEncodeError.
            #
            # Bug: https://github.com/PythonCharmers/python-future/issues/256
            # (This workaround can be removed once that is fixed.)
            except NameError as e:  # pragma: no cover
                if e.message == "global name 'exc' is not defined":
                    continue
                else:
                    raise

            self.assertEqual(os.fsdecode(bytesfn), fn)
