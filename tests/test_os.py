"""
Partial backport of Python 3.5's Lib/test/test_os.py with extra checks.
"""
from __future__ import unicode_literals
from __future__ import absolute_import

import unittest

from backports import os


class FSEncodingTests(unittest.TestCase):
    def test_nop(self):
        self.assertEqual(os.fsencode(b'abc\xff'), b'abc\xff')
        self.assertEqual(os.fsdecode('abc\u0141'), 'abc\u0141')

    def test_identity(self):
        for fn in ('unicode\u0141', 'latin\xe9', 'ascii'):
            try:
                bytesfn = os.fsencode(fn)
            except UnicodeEncodeError:
                continue
            self.assertEqual(os.fsdecode(bytesfn), fn)

    def test_non_utf(self):
        test_data = [
            b'non_ascii_12_\xe2\x82\xac',
            b'non_ascii_2_\xc3\xa6',
            b'non_ascii_5_\xcf\x86',
            b'non_ascii_4_\xc5\x81',
            b'non_utf8_decodable_\xff',
            b'non_ascii_3_\xc4\xb0',
            b'non_ascii_8_\xd8\x8c',
            b'non_ascii_7_\xd7\x90',
            b'non_utf8_decodable_3_\xed\xb4\x80',
            b'non_ascii_-\xc3\xa0\xc3\xb2\xc9\x98\xc5\x81\xc4\x9f',
            b'foo\xb1bar',
            b'non_cp932_decodable_\xe7w\xf0',
            b'non_ascii_11_\xc2\xa0',
            b'non_utf8_decodable_2_\xed\xb2\x80',
            b'non_ascii_9_\xd8\xaa',
            b'non_cp12_decodable_\x81\x98',
            b'non_ascii_10_\xe0\xb8\x81',
            b'non_ascii_6_\xd0\x9a',
            b'snow \xe2\x98\x83',
        ]
        for fn in test_data:
            self.assertEqual(fn, os.fsencode(os.fsdecode(fn)))

        fn = 'snow \u2603'
        self.assertEqual(fn, os.fsdecode(os.fsencode(fn)))


class FSEncodingTestsNoLocale(unittest.TestCase):
    def test_non_utf_without_locale(self):
        # this test will mimick a Linux without a proper locale and
        # ascii fsencoding: it spawns this script to rerun the tests in
        # a subprocess without a well define locale
        import sys
        import subprocess
        import os as real_os

        if 'linux' not in sys.platform:
            return

        cmd = sys.executable , real_os.path.abspath(__file__)

        # unset langiuage env variales to ensure we have a plain POSIX
        # locale and ascii FS encoding
        env = {'LANG': b'', 'LANGUAGE': b''}
        subprocess.check_output(cmd, env=env)


def _suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(FSEncodingTests))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='_suite', verbosity=2)
