#! /usr/bin/env python3

"""cppcheck-junit tests."""

from __future__ import absolute_import, division, print_function, unicode_literals

import sys
import unittest
from xml.etree import ElementTree

from cppcheck_junit import (CppcheckError, generate_single_success_test_suite,
                            generate_test_suite, parse_arguments, parse_cppcheck)


class ParseCppcheckTestCase(unittest.TestCase):
    def test_good(self):  # type: () -> None
        errors = parse_cppcheck('tests/cppcheck-out-good.xml')
        self.assertEqual(errors, {})

    def test_bad(self):  # type: () -> None
        file1 = 'bad.cpp'
        errors = parse_cppcheck('tests/cppcheck-out-bad.xml')

        self.assertEqual(errors[file1][0].file, file1)
        self.assertEqual(errors[file1][0].line, 4)
        self.assertEqual(errors[file1][0].message,
                         "Variable 'a' is assigned a value that is never used.")

        self.assertEqual(errors[file1][1].file, file1)
        self.assertEqual(errors[file1][1].line, 4)
        self.assertEqual(errors[file1][1].message,
                         "Array 'a[10]' accessed at index 10, which is out of bounds.")

    def test_no_location_element(self):  # type: () -> None
        file = ''
        errors = parse_cppcheck('tests/cppcheck-out-no-location-element.xml')

        self.assertEqual(len(errors), 1)
        error = errors[file][0]
        self.assertEqual(error.file, file)
        self.assertEqual(error.line, 0)
        self.assertEqual(
            error.message,
            'Too many #ifdef configurations - cppcheck only checks 12 configurations. '
            'Use --force to check all configurations. For more details, use '
            '--enable=information.')
        self.assertEqual(error.severity, 'information')

    def test_missing_include_no_location_element(self):  # type: () -> None
        file = ''
        errors = parse_cppcheck('tests/cppcheck-out-missing-include-no-location-element.xml')

        self.assertEqual(len(errors), 1)
        error = errors[file][0]
        self.assertEqual(error.file, file)
        self.assertEqual(error.line, 0)
        self.assertEqual(
            error.message,
            'Cppcheck cannot find all the include files (use --check-config for details)')
        self.assertEqual(error.severity, 'information')

    def test_bad_large(self):    # type: () -> None
        errors = parse_cppcheck('tests/cppcheck-out-bad-large.xml')
        self.assertEqual(len(errors), 43)

    def test_all(self):    # type: () -> None
        file1 = 'bad.cpp'
        file2 = 'bad2.cpp'
        errors = parse_cppcheck('tests/cppcheck-out-all.xml')

        self.assertEqual(errors[file1][0].file, file1)
        self.assertEqual(errors[file1][0].line, 4)
        self.assertEqual(errors[file1][0].message,
                         "Variable 'a' is assigned a value that is never used.")

        self.assertEqual(errors[file1][1].file, file1)
        self.assertEqual(errors[file1][1].line, 4)
        self.assertEqual(errors[file1][1].message,
                         "Array 'a[10]' accessed at index 10, which is out of bounds.")

        self.assertEqual(errors[file2][0].file, file2)
        self.assertEqual(errors[file2][0].line, 4)
        self.assertEqual(errors[file2][0].message,
                         "Variable 'a' is assigned a value that is never used.")

        self.assertEqual(errors[file2][1].file, file2)
        self.assertEqual(errors[file2][1].line, 4)
        self.assertEqual(errors[file2][1].message,
                         "Array 'a[10]' accessed at index 10, which is out of bounds.")

    def test_xml_version_1(self):  # type: () -> None
        with self.assertRaises(ValueError):
            parse_cppcheck('tests/cppcheck-out-bad-xml-version-1.xml')

    def test_file_not_found(self):  # type: () -> None
        with self.assertRaises(IOError):
            parse_cppcheck('tests/file_does_not_exist.xml')

    def test_malformed(self):  # type: () -> None
        with self.assertRaises(ElementTree.ParseError):
            parse_cppcheck('tests/cppcheck-out-malformed.xml')


class GenerateTestSuiteTestCase(unittest.TestCase):
    # Expected attributes from JUnit XSD
    #   ref: https://raw.githubusercontent.com/windyroad/JUnit-Schema/master/JUnit.xsd
    # @TODO: Better thing to do here would be to curl or otherwise access the
    #        spec above instead of hardcoding pieces of it here
    junit_testsuite_attributes = ['name', 'timestamp', 'hostname', 'tests', 'failures', 'errors', 'time']
    junit_testcase_attributes = ['name', 'classname', 'time']
    junit_error_attributes = ['type']

    def test_single(self):  # type: () -> None
        errors = {'file_name':
                  [CppcheckError('file_name',
                                 4,
                                 'error message',
                                 'severity',
                                 'error_id',
                                 'verbose error message')]}
        tree = generate_test_suite(errors)
        testsuite_element = tree.getroot()
        self.assertEqual(testsuite_element.get('errors'), str(1))
        self.assertEqual(testsuite_element.get('failures'), str(0))
        self.assertEqual(testsuite_element.get('tests'), str(1))
        # Check that testsuite element is compliant with the spec
        for required_attribute in self.junit_testsuite_attributes:
            self.assertTrue(required_attribute in testsuite_element.attrib.keys())

        testcase_element = testsuite_element.find('testcase')
        self.assertEqual(testcase_element.get('name'), 'file_name')
        # Check that test_case is compliant with the spec
        for required_attribute in self.junit_testcase_attributes:
            self.assertTrue(required_attribute in testcase_element.attrib.keys())

        error_element = testcase_element.find('error')
        self.assertEqual(error_element.get('file'), 'file_name')
        self.assertEqual(error_element.get('line'), str(4))
        self.assertEqual(error_element.get('message'), '4: (severity) error message')
        # Check that error element is compliant with the spec
        for required_attribute in self.junit_error_attributes:
            self.assertTrue(required_attribute in error_element.attrib.keys())

    def test_missing_file(self):  # type: () -> None
        errors = {'':
                  [CppcheckError(file='',
                                 line=0,
                                 message='Too many #ifdef configurations - cppcheck only checks '
                                         '12 configurations. Use --force to check all '
                                         'configurations. For more details, use '
                                         '--enable=information.',
                                 severity='information',
                                 error_id='toomanyconfigs',
                                 verbose='The checking of the file will be interrupted because '
                                         'there are too many #ifdef configurations. Checking of '
                                         'all #ifdef configurations can be forced by --force '
                                         'command line option or from GUI preferences. However '
                                         'that may increase the checking time. For more details, '
                                         'use --enable=information.')]}
        tree = generate_test_suite(errors)
        testsuite_element = tree.getroot()
        self.assertEqual(testsuite_element.get('errors'), str(1))
        self.assertEqual(testsuite_element.get('failures'), str(0))
        self.assertEqual(testsuite_element.get('tests'), str(1))
        # Check that testsuite element is compliant with the spec
        for required_attribute in self.junit_testsuite_attributes:
            self.assertTrue(required_attribute in testsuite_element.attrib.keys())

        testcase_element = testsuite_element.find('testcase')
        self.assertEqual(testcase_element.get('name'), '')
        # Check that test_case is compliant with the spec
        for required_attribute in self.junit_testcase_attributes:
            self.assertTrue(required_attribute in testcase_element.attrib.keys())

        error_element = testcase_element.find('error')
        self.assertEqual(error_element.get('file'), '')
        self.assertEqual(error_element.get('line'), str(0))
        self.assertEqual(error_element.get('message'),
                         '0: (information) Too many #ifdef configurations - cppcheck only checks '
                         '12 configurations. Use --force to check all '
                         'configurations. For more details, use '
                         '--enable=information.')
        # Check that error element is compliant with the spec
        for required_attribute in self.junit_error_attributes:
            self.assertTrue(required_attribute in error_element.attrib.keys())


class GenerateSingleSuccessTestSuite(unittest.TestCase):
    # Expected attributes from JUnit XSD
    #   ref: https://raw.githubusercontent.com/windyroad/JUnit-Schema/master/JUnit.xsd
    # @TODO: Better thing to do here would be to curl or otherwise access the
    #        spec above instead of hardcoding pieces of it here
    junit_testsuite_attributes = ['name', 'timestamp', 'hostname', 'tests', 'failures', 'errors', 'time']
    junit_testcase_attributes = ['name', 'classname', 'time']

    def test(self):  # type: () -> None
        tree = generate_single_success_test_suite()
        testsuite_element = tree.getroot()
        self.assertEqual(testsuite_element.get('tests'), str(1))
        self.assertEqual(testsuite_element.get('errors'), str(0))
        self.assertEqual(testsuite_element.get('failures'), str(0))
        # Check that testsuite element is compliant with the spec
        for required_attribute in self.junit_testsuite_attributes:
            self.assertTrue(required_attribute in testsuite_element.attrib.keys())

        testcase_element = testsuite_element.find('testcase')
        self.assertEqual(testcase_element.get('name'), 'Cppcheck success')
        # Check that test_case is compliant with the spec
        for required_attribute in self.junit_testcase_attributes:
            self.assertTrue(required_attribute in testcase_element.attrib.keys())


class ParseArgumentsTestCase(unittest.TestCase):
    def test_no_arguments(self):  # type: () -> None
        with self.assertRaises(SystemExit):
            # Suppress argparse stderr.
            class NullWriter:
                def write(self, s):    # type: (str) -> None
                    pass

            sys.stderr = NullWriter()
            parse_arguments()
