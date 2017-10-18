# coding: utf-8
"""
Additional test coverage, to supplement the backport of test_os.
"""
from __future__ import unicode_literals

import codecs
import os as real_os
import sys
from functools import partial

from backports import os

import unittest
from hypothesis import given, example
from hypothesis.strategies import text, binary


class ExtraCoverageTests(unittest.TestCase):
    """
    Basic tests just to fill some coverage gaps.
    """

    def _assertRaisesMessage(self, excClass, excMessage, callableObj):
        with self.assertRaises(excClass) as cm:
            callableObj()
        self.assertEqual(str(cm.exception), excMessage)

    def test_getenv(self):
        self.assertEqual(os.getenv('foo'), None)
        self.assertEqual(os.getenv('foo', 'bar'), 'bar')

        msg = ('unicode expected, not str' if sys.version_info < (3,) else
               'str expected, not bytes')
        self._assertRaisesMessage(TypeError, msg, lambda: os.getenv(b'foo'))
        self._assertRaisesMessage(TypeError, msg, lambda: os.getenv(b'foo', b'bar'))

    def test_getenvb(self):
        self.assertEqual(os.getenvb(b'foo'), None)
        self.assertEqual(os.getenvb(b'foo', b'bar'), b'bar')

        msg = ('bytes expected, not unicode' if sys.version_info < (3,) else
               'bytes expected, not str')
        self._assertRaisesMessage(TypeError, msg, lambda: os.getenvb('foo'))
        self._assertRaisesMessage(TypeError, msg, lambda: os.getenvb('foo', 'bar'))

    def test_popen_errors(self):
        self._assertRaisesMessage(
            TypeError, ("invalid cmd type (<type 'str'>, expected string)"
                        if sys.version_info < (3,) else
                        "invalid cmd type (<class 'bytes'>, expected string)"),
            lambda: os.popen(b'true'))

        self._assertRaisesMessage(
            ValueError, ("invalid mode u'x'" if sys.version_info < (3,) else
                         "invalid mode 'x'"),
            lambda: os.popen('true', mode='x'))

        for buffering in [0, None]:
            self._assertRaisesMessage(
                ValueError, 'popen() does not support unbuffered streams',
                lambda: os.popen('true', buffering=buffering))

    def test_popen_for_write(self):
        with os.popen('true', mode='w') as f:
            self.assertEqual(f.buffer.mode, 'wb')
        self.assertTrue(f.closed)

    def test_environ_copy(self):
        for environ in [os.environ, os.environb]:
            d = environ.copy()
            self.assertIsNot(d, environ)
            self.assertIsInstance(d, dict)
            self.assertEqual(d, environ)


# Example data:

HIGH_BYTES = (
    b'\x80\x81\x82\x83\x84\x85\x86\x87\x88\x89\x8a\x8b\x8c\x8d\x8e\x8f'
    b'\x90\x91\x92\x93\x94\x95\x96\x97\x98\x99\x9a\x9b\x9c\x9d\x9e\x9f'
    b'\xa0\xa1\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xab\xac\xad\xae\xaf'
    b'\xb0\xb1\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xbb\xbc\xbd\xbe\xbf'
    b'\xc0\xc1\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xcb\xcc\xcd\xce\xcf'
    b'\xd0\xd1\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xdb\xdc\xdd\xde\xdf'
    b'\xe0\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xeb\xec\xed\xee\xef'
    b'\xf0\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xfb\xfc\xfd\xfe\xff'
)

HIGH_SURROGATES = (
    '\udc80\udc81\udc82\udc83\udc84\udc85\udc86\udc87\udc88\udc89\udc8a\udc8b\udc8c\udc8d\udc8e\udc8f'
    '\udc90\udc91\udc92\udc93\udc94\udc95\udc96\udc97\udc98\udc99\udc9a\udc9b\udc9c\udc9d\udc9e\udc9f'
    '\udca0\udca1\udca2\udca3\udca4\udca5\udca6\udca7\udca8\udca9\udcaa\udcab\udcac\udcad\udcae\udcaf'
    '\udcb0\udcb1\udcb2\udcb3\udcb4\udcb5\udcb6\udcb7\udcb8\udcb9\udcba\udcbb\udcbc\udcbd\udcbe\udcbf'
    '\udcc0\udcc1\udcc2\udcc3\udcc4\udcc5\udcc6\udcc7\udcc8\udcc9\udcca\udccb\udccc\udccd\udcce\udccf'
    '\udcd0\udcd1\udcd2\udcd3\udcd4\udcd5\udcd6\udcd7\udcd8\udcd9\udcda\udcdb\udcdc\udcdd\udcde\udcdf'
    '\udce0\udce1\udce2\udce3\udce4\udce5\udce6\udce7\udce8\udce9\udcea\udceb\udcec\udced\udcee\udcef'
    '\udcf0\udcf1\udcf2\udcf3\udcf4\udcf5\udcf6\udcf7\udcf8\udcf9\udcfa\udcfb\udcfc\udcfd\udcfe\udcff'
)

# A U+DC80 surrogate encoded as (invalid) UTF-8.
#
# Python 3 correctly rejects this when encoding to or from UTF-8, but
# Python 2's UTF-8 codec is more lenient, and will happily pass it
# through (like Python 3's "surrogatepass" error handler does).
#
UTF8_ENCODED_SURROGATE = b'\xed\xb0\x80'


# Helper strategy: If the filesystem encoding is ASCII,
# limit the set of valid text to encode to ASCII too.
FILESYSTEM_IS_ASCII = codecs.lookup(sys.getfilesystemencoding()) == codecs.lookup('ascii')
ASCII = ''.join(chr(i) for i in range(128))
encodable_text = (partial(text, alphabet=ASCII) if FILESYSTEM_IS_ASCII else
                  text)


class ExtraFSEncodingTests(unittest.TestCase):

    def test_encode_surrogates(self):
        """
        Explicitly encode all the high byte surrogates to bytes.
        """
        self.assertEqual(os.fsencode(HIGH_SURROGATES), HIGH_BYTES)

    def test_decode_surrogates(self):
        """
        Explicitly decode all the high bytes to surrogates.
        """
        self.assertEqual(os.fsdecode(HIGH_BYTES), HIGH_SURROGATES)

    @given(encodable_text())
    @example(HIGH_SURROGATES)
    def test_text_roundtrip(self, s):
        self.assertEqual(os.fsdecode(os.fsencode(s)), s)

    @given(binary())
    @example(HIGH_BYTES)
    @example(UTF8_ENCODED_SURROGATE)
    def test_binary_roundtrip(self, b):
        self.assertEqual(os.fsencode(os.fsdecode(b)), b)

    def test_TypeError(self):
        def assertTypeError(value, expected_message):
            for f in [os.fsencode, os.fsdecode]:
                with self.assertRaises(TypeError) as cm:
                    f(value)
                self.assertEqual(str(cm.exception), expected_message)

        pre = 'expect bytes or {}, not '.format(
            'unicode' if sys.version_info < (3,) else 'str')
        assertTypeError(None, pre + 'NoneType')
        assertTypeError(5, pre + 'int')
        assertTypeError([], pre + 'list')
        assertTypeError((), pre + 'tuple')


@unittest.skipIf(sys.version_info < (3,), 'Python 3 only')
class TestFSEncodingAgainstPython3(unittest.TestCase):
    """
    On Python 3, the backported fsencode() / fsdecode() should match the standard library.
    """

    @given(encodable_text())
    @example(HIGH_SURROGATES)
    def test_encode_text(self, s):
        self.assertEqual(os.fsencode(s), real_os.fsencode(s))

    @given(binary())
    @example(HIGH_BYTES)
    @example(UTF8_ENCODED_SURROGATE)
    def test_decode_binary(self, b):
        self.assertEqual(os.fsdecode(b), real_os.fsdecode(b))

    @given(binary())
    @example(HIGH_BYTES)
    @example(UTF8_ENCODED_SURROGATE)
    def test_encode_binary(self, b):
        self.assertEqual(os.fsencode(b), real_os.fsencode(b))

    @given(text())
    @example(HIGH_SURROGATES)
    def test_decode_text(self, s):
        self.assertEqual(os.fsdecode(s), real_os.fsdecode(s))
