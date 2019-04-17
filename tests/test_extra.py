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
from hypothesis import assume, given, example
from hypothesis.strategies import text, binary

# SKIP_CONDITIONS:
IS_WIN = sys.platform.startswith("win")
IS_PY3 = sys.version_info[0] == 3

# Example data:

SURROGATE_ESCAPE_HIGH_BYTES = (
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

SURROGATE_PASS_HIGH_BYTES = (
    b'\xed\xb2\x80\xed\xb2\x81\xed\xb2\x82\xed\xb2\x83\xed\xb2\x84\xed'
    b'\xb2\x85\xed\xb2\x86\xed\xb2\x87\xed\xb2\x88\xed\xb2\x89\xed\xb2'
    b'\x8a\xed\xb2\x8b\xed\xb2\x8c\xed\xb2\x8d\xed\xb2\x8e\xed\xb2\x8f'
    b'\xed\xb2\x90\xed\xb2\x91\xed\xb2\x92\xed\xb2\x93\xed\xb2\x94\xed'
    b'\xb2\x95\xed\xb2\x96\xed\xb2\x97\xed\xb2\x98\xed\xb2\x99\xed\xb2'
    b'\x9a\xed\xb2\x9b\xed\xb2\x9c\xed\xb2\x9d\xed\xb2\x9e\xed\xb2\x9f'
    b'\xed\xb2\xa0\xed\xb2\xa1\xed\xb2\xa2\xed\xb2\xa3\xed\xb2\xa4\xed'
    b'\xb2\xa5\xed\xb2\xa6\xed\xb2\xa7\xed\xb2\xa8\xed\xb2\xa9\xed\xb2'
    b'\xaa\xed\xb2\xab\xed\xb2\xac\xed\xb2\xad\xed\xb2\xae\xed\xb2\xaf'
    b'\xed\xb2\xb0\xed\xb2\xb1\xed\xb2\xb2\xed\xb2\xb3\xed\xb2\xb4\xed'
    b'\xb2\xb5\xed\xb2\xb6\xed\xb2\xb7\xed\xb2\xb8\xed\xb2\xb9\xed\xb2'
    b'\xba\xed\xb2\xbb\xed\xb2\xbc\xed\xb2\xbd\xed\xb2\xbe\xed\xb2\xbf'
    b'\xed\xb3\x80\xed\xb3\x81\xed\xb3\x82\xed\xb3\x83\xed\xb3\x84\xed'
    b'\xb3\x85\xed\xb3\x86\xed\xb3\x87\xed\xb3\x88\xed\xb3\x89\xed\xb3'
    b'\x8a\xed\xb3\x8b\xed\xb3\x8c\xed\xb3\x8d\xed\xb3\x8e\xed\xb3\x8f'
    b'\xed\xb3\x90\xed\xb3\x91\xed\xb3\x92\xed\xb3\x93\xed\xb3\x94\xed'
    b'\xb3\x95\xed\xb3\x96\xed\xb3\x97\xed\xb3\x98\xed\xb3\x99\xed\xb3'
    b'\x9a\xed\xb3\x9b\xed\xb3\x9c\xed\xb3\x9d\xed\xb3\x9e\xed\xb3\x9f'
    b'\xed\xb3\xa0\xed\xb3\xa1\xed\xb3\xa2\xed\xb3\xa3\xed\xb3\xa4\xed'
    b'\xb3\xa5\xed\xb3\xa6\xed\xb3\xa7\xed\xb3\xa8\xed\xb3\xa9\xed\xb3'
    b'\xaa\xed\xb3\xab\xed\xb3\xac\xed\xb3\xad\xed\xb3\xae\xed\xb3\xaf'
    b'\xed\xb3\xb0\xed\xb3\xb1\xed\xb3\xb2\xed\xb3\xb3\xed\xb3\xb4\xed'
    b'\xb3\xb5\xed\xb3\xb6\xed\xb3\xb7\xed\xb3\xb8\xed\xb3\xb9\xed\xb3'
    b'\xba\xed\xb3\xbb\xed\xb3\xbc\xed\xb3\xbd\xed\xb3\xbe\xed\xb3\xbf'
)


# Use surrogate pass for encoding on windows on python 3+ to ensure
# we can decode them as the native decoder uses surrogate escape
if IS_WIN and IS_PY3:
    HIGH_BYTES = SURROGATE_PASS_HIGH_BYTES
else:
    HIGH_BYTES = SURROGATE_ESCAPE_HIGH_BYTES

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

    @unittest.skipIf(
        IS_PY3 and sys.version_info[:2] <= (3, 5) and IS_WIN,
        "Backport doesn't align with native implementation on win on or before python 3.5"
    )
    @given(binary())
    @example(HIGH_BYTES)
    @example(UTF8_ENCODED_SURROGATE)
    def test_binary_roundtrip(self, b):
        # in python 3 on windows, the native implementation of os.fsdecode
        # always relies on `surrogatepass` as the error handler, which means
        # it will fail on surrogates (which are not unicode compatible)
        # so if we fail to decode something under those circumstances we should
        # verify that the native implementation also fails.
        rt1 = None
        try:
            rt1 = os.fsdecode(b)
        except Exception as e:
            if IS_WIN and IS_PY3:
                self.assertRaises(type(e), real_os.fsdecode, b)
            else:
                raise
        else:
            try:
                roundtripped = os.fsencode(rt1)
            except Exception as e:
                if IS_WIN and IS_PY3:
                    self.assertRaises(type(e), real_os.fsencode, rt1)
                else:
                    raise
            else:
                self.assertEqual(roundtripped, b)

    def test_TypeError(self):
        def assertTypeError(value, expected_message):
            for f in [os.fsencode, os.fsdecode]:

                with self.assertRaises(TypeError) as cm:
                    f(value)
                self.assertEqual(str(cm.exception), expected_message)
        pre = 'expected {0}, bytes or os.PathLike object, not '.format(
            'unicode' if sys.version_info < (3,) else 'str'
        )
        assertTypeError(None, pre + 'NoneType')
        assertTypeError(5, pre + 'int')
        assertTypeError([], pre + 'list')
        assertTypeError((), pre + 'tuple')


@unittest.skipIf(sys.version_info < (3,), 'Python 3 only')
class TestAgainstPython3(unittest.TestCase):
    """
    On Python 3, the backported implementations should match the standard library.
    """

    @unittest.skipIf(
        IS_PY3 and sys.version_info[:2] <= (3, 5) and IS_WIN,
        "Backport doesn't align with native implementation on win on or before python 3.5"
    )
    @given(encodable_text())
    @example(HIGH_SURROGATES)
    def test_encode_text(self, s):
        self.assertEqual(os.fsencode(s), real_os.fsencode(s))

    @unittest.skipIf(
        IS_PY3 and sys.version_info[:2] <= (3, 5) and IS_WIN,
        "Backport doesn't align with native implementation on win on or before python 3.5"
    )
    @given(binary())
    @example(HIGH_BYTES)
    @example(UTF8_ENCODED_SURROGATE)
    def test_decode_binary(self, b):
        # Python 3 on windows will never be able to decode things
        # in the backported library that it can't also decode
        # in the original OS module implementation, so lets just catch
        # the exceptions thrown by the os module and expect them
        # to be raised by the backport
        try:
            real_os_val = real_os.fsdecode(b)
        except Exception as e:
            self.assertRaises(type(e), os.fsdecode, b)
        else:
            self.assertEqual(os.fsdecode(b), real_os_val)

    @given(binary())
    @example(HIGH_BYTES)
    @example(UTF8_ENCODED_SURROGATE)
    def test_encode_binary(self, b):
        self.assertEqual(os.fsencode(b), real_os.fsencode(b))

    @given(text())
    @example(HIGH_SURROGATES)
    def test_decode_text(self, s):
        self.assertEqual(os.fsdecode(s), real_os.fsdecode(s))
