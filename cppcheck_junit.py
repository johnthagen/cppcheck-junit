#!/usr/bin/env python3

"""Converts Cppcheck XML version 2 output to JUnit XML format."""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import collections
from datetime import datetime
import os
from socket import gethostname
import sys
from typing import Dict, List  # noqa: F401
from xml.etree import ElementTree

from exitstatus import ExitStatus


class CppcheckError(object):
    def __init__(self,
                 file,  # type: str
                 line,  # type: int
                 message,  # type: str
                 severity,  # type: str
                 error_id,  # type: str
                 verbose  # type: str
                 ):
        # type: (...) -> CppcheckError
        """Constructor.

        Args:
            file: File error originated on.
            line: Line error originated on.
            message: Error message.
            severity: Severity of the error.
            error_id: Unique identifier for the error.
            verbose: Verbose error message.
        """
        self.file = file
        self.line = line
        self.message = message
        self.severity = severity
        self.error_id = error_id
        self.verbose = verbose


def parse_arguments():
    # type: () -> argparse.Namespace
    parser = argparse.ArgumentParser(
        description='Converts Cppcheck XML version 2 to JUnit XML format.\n'
                    'Usage:\n'
                    '\t$ cppcheck --xml-version=2 --enable=all . 2> cppcheck-result.xml\n'
                    '\t$ cppcheck_junit cppcheck-result.xml cppcheck-junit.xml\n',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('input_file', type=str, help='Cppcheck XML version 2 stderr file.')
    parser.add_argument('output_file', type=str, help='JUnit XML output file.')
    return parser.parse_args()


def parse_cppcheck(file_name):
    # type: (str) -> Dict[str, List[CppcheckError]]
    """Parses a Cppcheck XML version 2 file.

    Args:
        file_name: Cppcheck XML file.

    Returns:
        Parsed errors grouped by file name.

    Raises:
        IOError: If file_name does not exist (More specifically, FileNotFoundError on Python 3).
        xml.etree.ElementTree.ParseError: If file_name is not a valid XML file.
        ValueError: If unsupported Cppcheck XML version.
    """
    root = ElementTree.parse(file_name).getroot()  # type: ElementTree.Element

    if (root.get('version') is None or
       int(root.get('version')) != 2):
        raise ValueError('Parser only supports Cppcheck XML version 2.  Use --xml-version=2.')

    error_root = root.find('errors')

    errors = collections.defaultdict(list)
    for error_element in error_root:
        location_element = error_element.find('location')  # type: ElementTree.Element
        if location_element is not None:
            file = location_element.get('file')
            line = int(location_element.get('line'))
        else:
            file = ''
            line = 0

        error = CppcheckError(file=file,
                              line=line,
                              message=error_element.get('msg'),
                              severity=error_element.get('severity'),
                              error_id=error_element.get('id'),
                              verbose=error_element.get('verbose'))
        errors[error.file].append(error)

    return errors


def generate_test_suite(errors):
    # type: (Dict[str, List[CppcheckError]]) -> ElementTree.ElementTree
    """Converts parsed Cppcheck errors into JUnit XML tree.

    Args:
        errors: Parsed cppcheck errors.

    Returns:
        XML test suite.
    """
    test_suite = ElementTree.Element('testsuite')
    test_suite.attrib['name'] = 'Cppcheck errors'
    test_suite.attrib['timestamp'] = datetime.isoformat(datetime.now())
    test_suite.attrib['hostname'] = gethostname()
    test_suite.attrib['tests'] = str(len(errors))
    test_suite.attrib['failures'] = str(0)
    test_suite.attrib['errors'] = str(len(errors))
    test_suite.attrib['time'] = str(1)

    for file_name, errors in errors.items():
        test_case = ElementTree.SubElement(test_suite,
                                           'testcase',
                                           name=os.path.relpath(
                                               file_name) if file_name else 'Cppcheck error',
                                           classname='Cppcheck error',
                                           time=str(1))
        for error in errors:
            ElementTree.SubElement(test_case,
                                   'error',
                                   type='',
                                   file=os.path.relpath(error.file) if error.file else '',
                                   line=str(error.line),
                                   message='{}: ({}) {}'.format(error.line,
                                                                error.severity,
                                                                error.message))

    return ElementTree.ElementTree(test_suite)


def generate_single_success_test_suite():
    # type: () -> ElementTree.ElementTree
    """Generates a single successful JUnit XML testcase."""
    test_suite = ElementTree.Element('testsuite')
    test_suite.attrib['name'] = 'Cppcheck errors'
    test_suite.attrib['timestamp'] = datetime.isoformat(datetime.now())
    test_suite.attrib['hostname'] = gethostname()
    test_suite.attrib['tests'] = str(1)
    test_suite.attrib['failures'] = str(0)
    test_suite.attrib['errors'] = str(0)
    test_suite.attrib['time'] = str(1)
    ElementTree.SubElement(test_suite,
                           'testcase',
                           name='Cppcheck success',
                           classname='Cppcheck success',
                           time=str(1))
    return ElementTree.ElementTree(test_suite)


def main():  # pragma: no cover
    # type: () -> ExitStatus
    """Main function.

    Returns:
        Exit code.
    """
    args = parse_arguments()

    try:
        errors = parse_cppcheck(args.input_file)
    except ValueError as e:
        print(str(e))
        return ExitStatus.failure
    except IOError as e:
        print(str(e))
        return ExitStatus.failure
    except ElementTree.ParseError as e:
        print('{} is a malformed XML file. Did you use --xml-version=2?\n{}'.format(
            args.input_file, e))
        return ExitStatus.failure

    if len(errors) > 0:
        tree = generate_test_suite(errors)
    else:
        tree = generate_single_success_test_suite()
    tree.write(args.output_file, encoding='utf-8', xml_declaration=True)

    return ExitStatus.success


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
