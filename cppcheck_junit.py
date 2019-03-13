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
                 id,  # type: str
                 verbose,  # type: str
                 cwe  # type: str
                 ):
        # type: (...) -> CppcheckError
        """Constructor.

        Args:
            file: File error originated on.
            line: Line error originated on.
            message: Error message.
            severity: Severity of the error.
            id: Unique identifier for the error.
            verbose: Verbose error message.
            cwe: CWE of found error
        """
        self.file = os.path.relpath(file) if file is not None else '[UNK]'
        self.line = line if line is not None else '0'
        self.message = message
        self.severity = severity
        self.id = id
        self.cwe = cwe
        self._verbose = verbose

    @property
    def file_with_line(self):
        return '{}:{}'.format(self.file, self.line)

    @property
    def verbose(self):
        return self._verbose if self._verbose else self.message


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
    # type: (str) -> List[CppcheckError]
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

    errors = []
    for error_element in error_root:
        location_elements = error_element.findall('location')  # type: List[ElementTree.Element]
        if location_elements:
            file_location = [(elem.get('file'), elem.get('line')) for elem in location_elements]
        else:
            file_location = [(None, None)]

        for file, line in file_location:
            error = CppcheckError(file=file,
                                  line=line,
                                  message=error_element.get('msg'),
                                  severity=error_element.get('severity'),
                                  id=error_element.get('id'),
                                  verbose=error_element.get('verbose'),
                                  cwe=error_element.get('cwe'))
            errors.append(error)
    return errors


def generate_root_element(tests_num, failures_num):
    test_suites = ElementTree.Element('testsuites')
    test_suites.attrib['name'] = 'Cppcheck errors'
    test_suites.attrib['id'] = datetime.isoformat(datetime.now())
    test_suites.attrib['tests'] = str(tests_num)
    test_suites.attrib['failures'] = str(failures_num)
    test_suites.attrib['errors'] = str(0)
    test_suites.attrib['time'] = str(1)

    test_suite = ElementTree.SubElement(test_suites,
                                        'testsuite',
                                        id="0",
                                        name="Cppcheck errors[ts]",
                                        classname='Cppcheck error[ts_c]',
                                        time=str(1))

    return test_suites, test_suite


def generate_test_cases(errors):
    # type: (Dict[str, List[CppcheckError]]) -> ElementTree.ElementTree
    """Converts parsed Cppcheck errors into JUnit XML tree.

    Args:
        errors: Parsed cppcheck errors.

    Returns:
        XML test suite.
    """

    root, test_suite = generate_root_element(len(errors), len(errors))

    for error in errors:
        test_case = ElementTree.SubElement(test_suite,
                                           'testcase',
                                           id=error.file_with_line,
                                           name=error.file_with_line)
        failure = ElementTree.SubElement(test_case,
                                         'failure',
                                         type=error.id,
                                         message=error.message)
        failure.text = '\n[{}] {}: {}\n{}\n'.format(error.severity, error.id, error.file_with_line, error.verbose)
    return ElementTree.ElementTree(root)


def generate_single_success_test_case():
    # type: () -> ElementTree.ElementTree
    """Generates a single successful JUnit XML testcase."""
    root, test_suite = generate_root_element(1, 0)

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
        tree = generate_test_cases(errors)
    else:
        tree = generate_single_success_test_case()
    tree.write(args.output_file, encoding='utf-8', xml_declaration=True)

    return ExitStatus.success


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main())
