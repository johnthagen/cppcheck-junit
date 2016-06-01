#! /usr/bin/env python3

"""cppcheck-junit tests."""

import sys
import unittest
from xml.etree import ElementTree

from cppcheck_junit import (CppcheckError, generate_single_success_test_suite,
                            generate_test_suite, parse_arguments, parse_cppcheck)


class ParseCppcheckTestCase(unittest.TestCase):
    def test_good(self):
        errors = parse_cppcheck('tests/cppcheck-out-good.xml')
        self.assertEqual(errors, {})

    def test_bad(self):
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

    def test_no_location_element(self):
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

    def test_bad_large(self):
        errors = parse_cppcheck('tests/cppcheck-out-bad-large.xml')
        self.assertEqual(len(errors), 43)

    def test_all(self):
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

    def test_xml_version_1(self):
        with self.assertRaises(ValueError):
            parse_cppcheck('tests/cppcheck-out-bad-xml-version-1.xml')

    def test_file_not_found(self):
        with self.assertRaises(IOError):
            parse_cppcheck('tests/file_does_not_exist.xml')

    def test_malformed(self):
        with self.assertRaises(ElementTree.ParseError):
            parse_cppcheck('tests/cppcheck-out-malformed.xml')


class GenerateTestSuiteTestCase(unittest.TestCase):
    def test_single(self):
        errors = {'file_name':
                  [CppcheckError('file_name',
                                 4,
                                 'error message',
                                 'severity',
                                 'error_id',
                                 'verbose error message')]}
        tree = generate_test_suite(errors)
        root = tree.getroot()
        self.assertEqual(root.get('errors'), str(1))
        self.assertEqual(root.get('failures'), str(0))
        self.assertEqual(root.get('tests'), str(1))

        test_case_element = root.find('testcase')
        self.assertEqual(test_case_element.get('name'), 'file_name')

        error_element = test_case_element.find('error')
        self.assertEqual(error_element.get('file'), 'file_name')
        self.assertEqual(error_element.get('line'), str(4))
        self.assertEqual(error_element.get('message'), '4: (severity) error message')


class GenerateSingleSuccessTestSuite(unittest.TestCase):
    def test(self):
        tree = generate_single_success_test_suite()
        root = tree.getroot()
        self.assertEqual(root.get('tests'), str(1))

        test_case_element = root.find('testcase')
        self.assertEqual(test_case_element.get('name'), 'Cppcheck success')


class ParseArgumentsTestCase(unittest.TestCase):
    def test_no_arguments(self):
        with self.assertRaises(SystemExit):
            # Suppress argparse stderr.
            class NullWriter:
                def write(self, s):
                    pass

            sys.stderr = NullWriter()
            parse_arguments()

if __name__ == '__main__':
    unittest.main()
