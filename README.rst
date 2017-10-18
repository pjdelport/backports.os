============
backports.os
============

This package provides backports of new features in Python's os_ module
under the backports_ namespace.

.. _os: https://docs.python.org/3.5/library/os.html
.. _backports: https://pypi.python.org/pypi/backports

.. image:: https://img.shields.io/pypi/v/backports.os.svg
    :target: https://pypi.python.org/pypi/backports.os

.. image:: https://img.shields.io/badge/source-GitHub-lightgrey.svg
    :target: https://github.com/pjdelport/backports.os

.. image:: https://img.shields.io/github/issues/pjdelport/backports.os.svg
    :target: https://github.com/pjdelport/backports.os/issues?q=is:open

.. image:: https://travis-ci.org/pjdelport/backports.os.svg?branch=master
    :target: https://travis-ci.org/pjdelport/backports.os

.. image:: https://codecov.io/github/pjdelport/backports.os/coverage.svg?branch=master
    :target: https://codecov.io/github/pjdelport/backports.os?branch=master


Supported Python versions
=========================

* CPython: 2.7, 3.4, 3.5, 3.6
* PyPy, PyPy3


Backported functionality
========================

Changed in Python 3:

* `environ`_
* `getenv`_
* `popen`_

.. _`environ`: https://docs.python.org/3.5/library/os.html#os.environ
.. _`getenv`: https://docs.python.org/3.5/library/os.html#os.getenv
.. _`popen`: https://docs.python.org/3.5/library/os.html#os.popen

New in Python 3.2:

* `environb`_
* `fsdecode`_
* `fsencode`_
* `get_exec_path`_
* `getenvb`_
* `supports_bytes_environ`_

.. _`environb`: https://docs.python.org/3.5/library/os.html#os.environb
.. _`fsdecode`: https://docs.python.org/3.5/library/os.html#os.fsdecode
.. _`fsencode`: https://docs.python.org/3.5/library/os.html#os.fsencode
.. _`get_exec_path`: https://docs.python.org/3.5/library/os.html#os.get_exec_path
.. _`getenvb`: https://docs.python.org/3.5/library/os.html#os.getenvb
.. _`supports_bytes_environ`: https://docs.python.org/3.5/library/os.html#os.supports_bytes_environ


Contributing
============

See `<HACKING.rst>`__.
