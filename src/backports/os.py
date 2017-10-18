"""
Partial backport of new functionality in Python 3.5's os module:

Changed in Python 3:

    environ
    getenv
    popen

New in Python 3.2:

    environb
    fsdecode
    fsencode
    get_exec_path
    getenvb
    supports_bytes_environ

Backport modifications are marked with "XXX backport" and "TODO backport".
"""
from __future__ import absolute_import, unicode_literals

import sys

# XXX backport: unicode on Python 2
_str = unicode if sys.version_info < (3,) else str

# XXX backport: Use backported surrogateescape for Python 2
# TODO backport: Find a way to do this without pulling in the entire future package?
if sys.version_info < (3,):
    from future.utils.surrogateescape import register_surrogateescape
    register_surrogateescape()


# XXX backport: This invalid_utf8_indexes() helper is shamelessly copied from
# Bob Ippolito's pyutf8 package (pyutf8/ref.py), in order to help support the
# Python 2 UTF-8 decoding hack in fsdecode() below.
#
# URL: https://github.com/etrepum/pyutf8/blob/master/pyutf8/ref.py
#
def _invalid_utf8_indexes(bytes):
    skips = []
    i = 0
    len_bytes = len(bytes)
    while i < len_bytes:
        c1 = bytes[i]
        if c1 < 0x80:
            # U+0000 - U+007F - 7 bits
            i += 1
            continue
        try:
            c2 = bytes[i + 1]
            if ((c1 & 0xE0 == 0xC0) and (c2 & 0xC0 == 0x80)):
                # U+0080 - U+07FF - 11 bits
                c = (((c1 & 0x1F) << 6) |
                     (c2 & 0x3F))
                if c < 0x80:
                    # Overlong encoding
                    skips.extend([i, i + 1])
                i += 2
                continue
            c3 = bytes[i + 2]
            if ((c1 & 0xF0 == 0xE0) and
                (c2 & 0xC0 == 0x80) and
                (c3 & 0xC0 == 0x80)):
                # U+0800 - U+FFFF - 16 bits
                c = (((((c1 & 0x0F) << 6) |
                       (c2 & 0x3F)) << 6) |
                     (c3 & 0x3f))
                if ((c < 0x800) or (0xD800 <= c <= 0xDFFF)):
                    # Overlong encoding or surrogate.
                    skips.extend([i, i + 1, i + 2])
                i += 3
                continue
            c4 = bytes[i + 3]
            if ((c1 & 0xF8 == 0xF0) and
                (c2 & 0xC0 == 0x80) and
                (c3 & 0xC0 == 0x80) and
                (c4 & 0xC0 == 0x80)):
                # U+10000 - U+10FFFF - 21 bits
                c = (((((((c1 & 0x0F) << 6) |
                         (c2 & 0x3F)) << 6) |
                       (c3 & 0x3F)) << 6) |
                     (c4 & 0x3F))
                if (c < 0x10000) or (c > 0x10FFFF):
                    # Overlong encoding or invalid code point.
                    skips.extend([i, i + 1, i + 2, i + 3])
                i += 4
                continue
        except IndexError:
            pass
        skips.append(i)
        i += 1
    return skips


# XXX backport: Another helper to support the Python 2 UTF-8 decoding hack.
def _chunks(b, indexes):
    i = 0
    for j in indexes:
        yield b[i:j]
        yield b[j:j + 1]
        i = j + 1
    yield b[i:]


_names = sys.builtin_module_names

# Note:  more names are added to __all__ later.
__all__ = ["altsep", "curdir", "pardir", "sep", "pathsep", "linesep",
           "defpath", "name", "path", "devnull", "SEEK_SET", "SEEK_CUR",
           "SEEK_END", "fsencode", "fsdecode", "get_exec_path", "fdopen",
           "popen", "extsep"]

def _get_exports_list(module):
    try:
        return list(module.__all__)
    except AttributeError:
        return [n for n in dir(module) if n[0] != '_']

# Any new dependencies of the os module and/or changes in path separator
# requires updating importlib as well.
if 'posix' in _names:
    name = 'posix'
    linesep = '\n'
    from posix import *
    try:
        from posix import _exit
        __all__.append('_exit')
    except ImportError:
        pass
    import posixpath as path

    try:
        from posix import _have_functions
    except ImportError:
        pass

    import posix
    __all__.extend(_get_exports_list(posix))
    del posix

elif 'nt' in _names:
    name = 'nt'
    linesep = '\r\n'
    from nt import *
    try:
        from nt import _exit
        __all__.append('_exit')
    except ImportError:
        pass
    import ntpath as path

    import nt
    __all__.extend(_get_exports_list(nt))
    del nt

    try:
        from nt import _have_functions
    except ImportError:
        pass

elif 'ce' in _names:
    name = 'ce'
    linesep = '\r\n'
    from ce import *
    try:
        from ce import _exit
        __all__.append('_exit')
    except ImportError:
        pass
    # We can use the standard Windows path.
    import ntpath as path

    import ce
    __all__.extend(_get_exports_list(ce))
    del ce

    try:
        from ce import _have_functions
    except ImportError:
        pass

else:
    raise ImportError('no os specific module found')

# XXX backport: Don't actually modify sys.modules here.
# sys.modules['os.path'] = path

from os.path import (curdir, pardir, sep, pathsep, defpath, extsep, altsep,
    devnull)

del _names


# Make sure os.environ exists, at least
try:
    environ
except NameError:
    environ = {}


def get_exec_path(env=None):
    """Returns the sequence of directories that will be searched for the
    named executable (similar to a shell) when launching a process.

    *env* must be an environment variable dict or None.  If *env* is None,
    os.environ will be used.
    """
    # Use a local import instead of a global import to limit the number of
    # modules loaded at startup: the os module is always loaded at startup by
    # Python. It may also avoid a bootstrap issue.
    import warnings

    if env is None:
        env = environ

    # {b'PATH': ...}.get('PATH') and {'PATH': ...}.get(b'PATH') emit a
    # BytesWarning when using python -b or python -bb: ignore the warning
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", BytesWarning)

        try:
            path_list = env.get('PATH')
        except TypeError:
            path_list = None

        if supports_bytes_environ:

            # XXX backport: Python 2 folds text and binary to the same key,
            # so the following is not possible.
            if (3,) <= sys.version_info:
                try:
                    path_listb = env[b'PATH']
                except (KeyError, TypeError):
                    pass
                else:
                    if path_list is not None:
                        raise ValueError(
                            "env cannot contain 'PATH' and b'PATH' keys")
                    path_list = path_listb

            if path_list is not None and isinstance(path_list, bytes):
                path_list = fsdecode(path_list)

    if path_list is None:
        path_list = defpath
    return path_list.split(pathsep)


# Change environ to automatically call putenv(), unsetenv if they exist.
# XXX backport: Python 3.3 moves ABCs from collections to collections.abc
if sys.version_info < (3, 3):
    from collections import MutableMapping
else:
    from collections.abc import MutableMapping


class _Environ(MutableMapping):
    def __init__(self, data, encodekey, decodekey, encodevalue, decodevalue, putenv, unsetenv):
        self.encodekey = encodekey
        self.decodekey = decodekey
        self.encodevalue = encodevalue
        self.decodevalue = decodevalue
        self.putenv = putenv
        self.unsetenv = unsetenv
        self._data = data

    def __getitem__(self, key):
        try:
            value = self._data[self.encodekey(key)]
        except KeyError:
            # raise KeyError with the original key value
            # XXX backport: raise KeyError(key) from None
            raise KeyError(key)
        return self.decodevalue(value)

    def __setitem__(self, key, value):
        key = self.encodekey(key)
        value = self.encodevalue(value)
        self.putenv(key, value)
        self._data[key] = value

    def __delitem__(self, key):
        encodedkey = self.encodekey(key)
        self.unsetenv(encodedkey)
        try:
            del self._data[encodedkey]
        except KeyError:
            # raise KeyError with the original key value
            # XXX backport: raise KeyError(key) from None
            raise KeyError(key)

    def __iter__(self):
        for key in self._data:
            yield self.decodekey(key)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return 'environ({{{}}})'.format(', '.join(
            ('{!r}: {!r}'.format(self.decodekey(key), self.decodevalue(value))
            for key, value in self._data.items())))

    def copy(self):
        return dict(self)

    def setdefault(self, key, value):
        if key not in self:
            self[key] = value
        return self[key]

try:
    _putenv = putenv
except NameError:
    _putenv = lambda key, value: None
else:
    if "putenv" not in __all__:
        __all__.append("putenv")

try:
    _unsetenv = unsetenv
except NameError:
    _unsetenv = lambda key: _putenv(key, "")
else:
    if "unsetenv" not in __all__:
        __all__.append("unsetenv")

def _createenviron():
    if name == 'nt':
        # Where Env Var Names Must Be UPPERCASE
        def check_str(value):
            if not isinstance(value, _str):
                raise TypeError("{_str} expected, not {}".format(type(value).__name__,
                                                                 _str=_str.__name__))
            return value
        encode = check_str
        decode = _str
        def encodekey(key):
            return encode(key).upper()
        data = {}
        for key, value in environ.items():
            data[encodekey(key)] = value
    else:
        # Where Env Var Names Can Be Mixed Case
        encoding = sys.getfilesystemencoding()
        def encode(value):
            if not isinstance(value, _str):
                raise TypeError("{_str} expected, not {}".format(type(value).__name__,
                                                                 _str=_str.__name__))
            return value.encode(encoding, 'surrogateescape')
        def decode(value):
            return value.decode(encoding, 'surrogateescape')
        encodekey = encode
        data = environ
    return _Environ(data,
        encodekey, decode,
        encode, decode,
        _putenv, _unsetenv)

# unicode environ
environ = _createenviron()
del _createenviron


def getenv(key, default=None):
    """Get an environment variable, return None if it doesn't exist.
    The optional second argument can specify an alternate default.
    key, default and the result are str."""
    return environ.get(key, default)

supports_bytes_environ = (name != 'nt')
__all__.extend(("getenv", "supports_bytes_environ"))

if supports_bytes_environ:
    def _check_bytes(value):
        if not isinstance(value, bytes):
            raise TypeError("bytes expected, not %s" % type(value).__name__)
        return value

    # bytes environ
    environb = _Environ(environ._data,
        _check_bytes, bytes,
        _check_bytes, bytes,
        _putenv, _unsetenv)
    del _check_bytes

    def getenvb(key, default=None):
        """Get an environment variable, return None if it doesn't exist.
        The optional second argument can specify an alternate default.
        key, default and the result are bytes."""
        return environb.get(key, default)

    __all__.extend(("environb", "getenvb"))

def _fscodec():
    encoding = sys.getfilesystemencoding()
    if encoding == 'mbcs':
        errors = 'strict'
    else:
        errors = 'surrogateescape'

    # XXX backport: Do we need to hack around Python 2's UTF-8 codec?
    import codecs  # Use codecs.lookup() for name normalisation.
    _HACK_AROUND_PY2_UTF8 = (sys.version_info < (3,) and
                             codecs.lookup(encoding) == codecs.lookup('utf-8'))
    # Do we need to hack around Python 2's ASCII codec error handler behaviour?
    _HACK_AROUND_PY2_ASCII = (sys.version_info < (3,) and
                              codecs.lookup(encoding) == codecs.lookup('ascii'))

    # XXX backport: chr(octet) became bytes([octet])
    _byte = chr if sys.version_info < (3,) else lambda i: bytes([i])

    def fsencode(filename):
        """
        Encode filename to the filesystem encoding with 'surrogateescape' error
        handler, return bytes unchanged. On Windows, use 'strict' error handler if
        the file system encoding is 'mbcs' (which is the default encoding).
        """
        if isinstance(filename, bytes):
            return filename
        elif isinstance(filename, _str):
            if _HACK_AROUND_PY2_UTF8 or _HACK_AROUND_PY2_ASCII:
                # XXX backport: Unlike Python 3, Python 2's UTF-8 codec does not
                # consider surrogate codepoints invalid, so the surrogateescape
                # error handler never gets invoked to encode them back into high
                # bytes.
                #
                # This code hacks around that by manually encoding the surrogate
                # codepoints to high bytes, without relying on surrogateescape.
                #
                # As a *separate* issue to the above, Python2's ASCII codec has
                # a different problem: it correctly invokes the surrogateescape
                # error handler, but then seems to do additional strict
                # validation (?) on the interim surrogate-decoded Unicode buffer
                # returned by surrogateescape, and then fails with a
                # UnicodeEncodeError anyway.
                #
                # The fix for that happens to be the same (manual encoding),
                # even though the two causes are quite different.
                #
                return b''.join(
                    (_byte(ord(c) - 0xDC00) if 0xDC00 <= ord(c) <= 0xDCFF else
                     c.encode(encoding))
                    for c in filename)
            else:
                return filename.encode(encoding, errors)
        else:
            # XXX backport: unicode instead of str for Python 2
            raise TypeError("expect bytes or {_str}, not {}".format(type(filename).__name__,
                                                                    _str=_str.__name__, ))

    def fsdecode(filename):
        """
        Decode filename from the filesystem encoding with 'surrogateescape' error
        handler, return str unchanged. On Windows, use 'strict' error handler if
        the file system encoding is 'mbcs' (which is the default encoding).
        """
        if isinstance(filename, _str):
            return filename
        elif isinstance(filename, bytes):
            if _HACK_AROUND_PY2_UTF8:
                # XXX backport: See the remarks in fsencode() above.
                #
                # This case is slightly trickier: Python 2 will invoke the
                # surrogateescape error handler for most bad high byte
                # sequences, *except* for full UTF-8 sequences that happen to
                # decode to surrogate codepoints.
                #
                # For decoding, it's not trivial to sidestep the UTF-8 codec
                # only for surrogates like fsencode() does, but as a hack we can
                # split the input into separate chunks around each invalid byte,
                # decode the chunks separately, and join the results.
                #
                # This prevents Python 2's UTF-8 codec from seeing the encoded
                # surrogate sequences as valid, which lets surrogateescape take
                # over and escape the individual bytes.
                #
                # TODO: Improve this.
                #
                from array import array
                indexes = _invalid_utf8_indexes(array(str('B'), filename))
                return ''.join(chunk.decode(encoding, errors)
                               for chunk in _chunks(filename, indexes))
            else:
                return filename.decode(encoding, errors)
        else:
            # XXX backport: unicode instead of str for Python 2
            raise TypeError("expect bytes or {_str}, not {}".format(type(filename).__name__,
                                                                    _str=_str.__name__, ))

    return fsencode, fsdecode

fsencode, fsdecode = _fscodec()
del _fscodec


# Supply os.popen()
def popen(cmd, mode="r", buffering=-1):
    if not isinstance(cmd, _str):
        raise TypeError("invalid cmd type (%s, expected string)" % type(cmd))
    if mode not in ("r", "w"):
        raise ValueError("invalid mode %r" % mode)
    if buffering == 0 or buffering is None:
        raise ValueError("popen() does not support unbuffered streams")
    import subprocess, io

    # XXX backport: In Python 2, proc's stdout/stderr are raw files.
    # To work with TextIOWrapper, they must be wrapped in an io stream first.
    def _py2_wrap(f):
        return (io.open(f.fileno(), mode=f.mode)
                if sys.version_info < (3,) else f)

    if mode == "r":
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdout=subprocess.PIPE,
                                bufsize=buffering)
        return _wrap_close(io.TextIOWrapper(_py2_wrap(proc.stdout)), proc)
    else:
        proc = subprocess.Popen(cmd,
                                shell=True,
                                stdin=subprocess.PIPE,
                                bufsize=buffering)
        return _wrap_close(io.TextIOWrapper(_py2_wrap(proc.stdin)), proc)

# Helper for popen() -- a proxy for a file whose close waits for the process
class _wrap_close:
    def __init__(self, stream, proc):
        self._stream = stream
        self._proc = proc
    def close(self):
        self._stream.close()
        returncode = self._proc.wait()
        if returncode == 0:
            return None
        if name == 'nt':
            return returncode
        else:
            return returncode << 8  # Shift left to match old behavior
    def __enter__(self):
        return self
    def __exit__(self, *args):
        self.close()
    def __getattr__(self, name):
        return getattr(self._stream, name)
    def __iter__(self):
        return iter(self._stream)
