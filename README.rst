cppcheck JUnit Converter
========================

.. image:: https://travis-ci.org/johnthagen/cppcheck-junit.svg
    :target: https://travis-ci.org/johnthagen/cppcheck-junit

.. image:: https://codecov.io/github/johnthagen/clion-cppcheck/coverage.svg
    :target: https://codecov.io/github/johnthagen/clion-cppcheck

.. image:: https://img.shields.io/pypi/v/cppcheck-junit.svg
    :target: https://pypi.python.org/pypi/cppcheck-junit

.. image:: https://img.shields.io/pypi/pyversions/cppcheck-junit.svg
    :target: https://pypi.python.org/pypi/cppcheck-junit/

.. image:: https://img.shields.io/pypi/dd/cppcheck-junit.svg
    :target: https://pypi.python.org/pypi/cppcheck-junit/

Tool that converts `cppcheck <http://cppcheck.sourceforge.net/>`_ XML output to JUnit XML format.
Use on your CI servers to get more helpful feedback.

Installation
------------

You can install, upgrade, and uninstall ``cppcheck-junit`` with these commands:

.. code:: shell-session

    $ pip install cppcheck-junit
    $ pip install --upgrade cppcheck-junit
    $ pip uninstall cppcheck-junit

Usage
-----
Enable XML version 2 output, enable all message, and redirect ``cppcheck`` ``stderr`` to a file:

.. code:: shell-session

    $ cppcheck --xml-version=2 --enable=all . 2> cppcheck-result.xml

Convert it to JUnit XML format:

.. code:: shell-session

    $ cppcheck_junit cppcheck-result.xml cppcheck-junit.xml

Releases
--------

0.2.0 - 2016-01-28
^^^^^^^^^^^^^^^^^^

Added severity to JUnit message, improved help description, handle XML parsing errors.

0.1.0 - 2015-11-15
^^^^^^^^^^^^^^^^^^

First release.