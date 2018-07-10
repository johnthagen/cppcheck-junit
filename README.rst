cppcheck JUnit Converter
========================

.. image:: https://travis-ci.org/johnthagen/cppcheck-junit.svg
    :target: https://travis-ci.org/johnthagen/cppcheck-junit

.. image:: https://codeclimate.com/github/johnthagen/cppcheck-junit/badges/gpa.svg
   :target: https://codeclimate.com/github/johnthagen/cppcheck-junit

.. image:: https://codeclimate.com/github/johnthagen/cppcheck-junit/badges/issue_count.svg
   :target: https://codeclimate.com/github/johnthagen/cppcheck-junit

.. image:: https://codecov.io/github/johnthagen/cppcheck-junit/coverage.svg
    :target: https://codecov.io/github/johnthagen/cppcheck-junit

.. image:: https://img.shields.io/pypi/v/cppcheck-junit.svg
    :target: https://pypi.python.org/pypi/cppcheck-junit

.. image:: https://img.shields.io/pypi/status/cppcheck-junit.svg
    :target: https://pypi.python.org/pypi/cppcheck-junit

.. image:: https://img.shields.io/pypi/pyversions/cppcheck-junit.svg
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
Enable XML version 2 output, enable additional rules (for example ``all``), and redirect
``cppcheck`` ``stderr`` to a file:

.. code:: shell-session

    $ cppcheck --xml-version=2 --enable=all . 2> cppcheck-result.xml

Convert it to JUnit XML format:

.. code:: shell-session

    $ cppcheck_junit cppcheck-result.xml cppcheck-junit.xml

If no ``cppcheck`` errors are generated, a single ``"Cppcheck success"`` test case is
output so that CI tools like Bamboo will not fail on the JUnit task.

Releases
--------

1.6.0 - 2018-07-09
^^^^^^^^^^^^^^^^^^

Drop Python 3.3 and support Python 3.7.

1.5.0 - 2017-10-18
^^^^^^^^^^^^^^^^^^

Fix Bamboo support by always filling in ``name`` and ``classname`` attributes on JUnit error
test cases.

1.4.0 - 2017-06-14
^^^^^^^^^^^^^^^^^^

Expand JUnit schema support by adding in some missing fields.

1.3.0 - 2016-12-31
^^^^^^^^^^^^^^^^^^

Support Python 3.6.

1.2.0 - 2016-07-27
^^^^^^^^^^^^^^^^^^

Actually handle ``cppcheck`` errors that don't have a ``<location>`` tag.
Update test suite to use ``tox``.

1.1.2 - 2016-04-13
^^^^^^^^^^^^^^^^^^

Handle ``cppcheck`` errors that don't have a ``<location>`` tag.

1.1.1 - 2016-04-11
^^^^^^^^^^^^^^^^^^

Fix ``requirements.txt`` include for ``setup.py``.

1.1.0 - 2016-04-11
^^^^^^^^^^^^^^^^^^

If no ``cppcheck`` errors are parsed, output a single success test case to satisfy Bamboo.

1.0.0 - 2016-02-15
^^^^^^^^^^^^^^^^^^

Release 1.0.0.  Increase test coverage.

0.2.0 - 2016-01-28
^^^^^^^^^^^^^^^^^^

Added severity to JUnit message, improved help description, handle XML parsing errors.

0.1.0 - 2015-11-15
^^^^^^^^^^^^^^^^^^

First release.