#! /usr/bin/env python3

"""cppcheck-junit tests."""

from __future__ import absolute_import, division, print_function, unicode_literals

from copy import deepcopy
import sys
import unittest
from xml.etree import ElementTree

from cppcheck_junit import (
    CppcheckError,
    CppcheckLocation,
    generate_test_case,
    generate_test_error,
    generate_test_suite,
    parse_arguments,
    parse_cppcheck,
)


class ParseCppcheckTestCase(unittest.TestCase):
    def test_good(self) -> None:
        errors = parse_cppcheck("tests/cppcheck-out-good.xml")
        self.assertEqual(errors, {})

    def test_bad(self) -> None:
        file1 = "bad.cpp"
        errors = parse_cppcheck("tests/cppcheck-out-bad.xml")

        self.assertEqual(errors[file1][0].file, file1)
        self.assertEqual(errors[file1][0].locations[0].line, 4)
        self.assertEqual(
            errors[file1][0].message, "Variable 'a' is assigned a value that is never used."
        )

        self.assertEqual(errors[file1][1].file, file1)
        self.assertEqual(errors[file1][1].locations[0].line, 4)
        self.assertEqual(
            errors[file1][1].message, "Array 'a[10]' accessed at index 10, which is out of bounds."
        )

    def test_no_file_no_location(self) -> None:
        errors = parse_cppcheck("tests/cppcheck-out-no-location-element.xml")

        self.assertEqual(len(errors), 1)
        error = errors[""][0]
        self.assertEqual(error.file, "")
        self.assertEqual(error.locations, [])
        self.assertEqual(
            error.message,
            "Too many #ifdef configurations - cppcheck only checks 12 configurations. "
            "Use --force to check all configurations. For more details, use "
            "--enable=information.",
        )
        self.assertEqual(error.severity, "information")
        self.assertEqual(error.error_id, "toomanyconfigs")

    def test_bad_large(self) -> None:
        errors = parse_cppcheck("tests/cppcheck-out-bad-large.xml")
        self.assertEqual(len(errors), 43)

    def test_all(self) -> None:
        file1 = "bad.cpp"
        file2 = "bad2.cpp"
        errors = parse_cppcheck("tests/cppcheck-out-all.xml")

        self.assertEqual(errors[file1][0].file, file1)
        self.assertEqual(errors[file1][0].locations[0].line, 4)
        self.assertEqual(
            errors[file1][0].message, "Variable 'a' is assigned a value that is never used."
        )

        self.assertEqual(errors[file1][1].file, file1)
        self.assertEqual(errors[file1][1].locations[0].line, 4)
        self.assertEqual(
            errors[file1][1].message, "Array 'a[10]' accessed at index 10, which is out of bounds."
        )

        self.assertEqual(errors[file2][0].file, file2)
        self.assertEqual(errors[file2][0].locations[0].line, 4)
        self.assertEqual(
            errors[file2][0].message, "Variable 'a' is assigned a value that is never used."
        )

        self.assertEqual(errors[file2][1].file, file2)
        self.assertEqual(errors[file2][1].locations[0].line, 4)
        self.assertEqual(
            errors[file2][1].message, "Array 'a[10]' accessed at index 10, which is out of bounds."
        )

    def test_xml_version_1(self) -> None:
        with self.assertRaises(ValueError):
            parse_cppcheck("tests/cppcheck-out-bad-xml-version-1.xml")

    def test_file_not_found(self) -> None:
        with self.assertRaises(IOError):
            parse_cppcheck("tests/file_does_not_exist.xml")

    def test_malformed(self) -> None:
        with self.assertRaises(ElementTree.ParseError):
            parse_cppcheck("tests/cppcheck-out-malformed.xml")

    def test_malformed_no_errors(self) -> None:
        errors = parse_cppcheck("tests/cppcheck-malformed-no-errors.xml")
        self.assertEqual(errors, {})


class GenerateTestError(unittest.TestCase):
    basic_error = CppcheckError("file", [], "message", "severity", "error_id", "verbose")

    def test_no_location(self) -> None:
        cppcheck_error = deepcopy(self.basic_error)
        error = generate_test_error(cppcheck_error)
        self.assertEqual(error.type, "severity:error_id")
        self.assertEqual(error.message, "message")
        self.assertEqual(error.text, "verbose")

    def test_location_no_info(self) -> None:
        cppcheck_error = deepcopy(self.basic_error)
        cppcheck_error.locations = [CppcheckLocation("file1", 1, 0, "")]
        error = generate_test_error(cppcheck_error)
        self.assertEqual(error.type, "severity:error_id")
        self.assertEqual(error.message, "message")
        self.assertEqual(error.text, "file1:1:0: verbose")

    def test_location_with_info(self) -> None:
        cppcheck_error = deepcopy(self.basic_error)
        cppcheck_error.locations = [CppcheckLocation("file1", 1, 0, "info")]
        error = generate_test_error(cppcheck_error)
        self.assertEqual(error.type, "severity:error_id")
        self.assertEqual(error.message, "message")
        self.assertEqual(error.text, "verbose\nfile1:1:0: info")

    def test_locations(self) -> None:
        cppcheck_error = deepcopy(self.basic_error)
        cppcheck_error.locations = [
            CppcheckLocation("file1", 1, 0, "info"),
            CppcheckLocation("file2", 2, 0, "info"),
        ]
        error = generate_test_error(cppcheck_error)
        self.assertEqual(error.type, "severity:error_id")
        self.assertEqual(error.message, "message")
        self.assertEqual(error.text, "verbose\nfile1:1:0: info\nfile2:2:0: info")


class GenerateTestCase(unittest.TestCase):
    def test_no_name(self) -> None:
        testcase = generate_test_case("", "class", [])
        self.assertEqual(testcase.name, "Cppcheck")
        self.assertEqual(testcase.classname, "class")

    def test_with_name(self) -> None:
        testcase = generate_test_case("name", "class", [])
        self.assertEqual(testcase.name, "name")
        self.assertEqual(testcase.classname, "class")


class GenerateTestSuite(unittest.TestCase):
    error = CppcheckError("", [], "", "", "", "")

    def test_no_error(self) -> None:
        testsuite = generate_test_suite({})
        self.assertEqual(testsuite.errors, 0)
        self.assertEqual(testsuite.failures, 0)
        self.assertEqual(testsuite.skipped, 0)
        self.assertEqual(testsuite.tests, 1)

    def test_single(self) -> None:
        errors = {"file": [self.error]}
        testsuite = generate_test_suite(errors)
        self.assertEqual(testsuite.errors, 1)
        self.assertEqual(testsuite.failures, 0)
        self.assertEqual(testsuite.skipped, 0)
        self.assertEqual(testsuite.tests, 1)

    def test_single_multiple_error(self) -> None:
        errors = {"file": [self.error, self.error]}
        testsuite = generate_test_suite(errors)
        self.assertEqual(testsuite.errors, 2)
        self.assertEqual(testsuite.failures, 0)
        self.assertEqual(testsuite.skipped, 0)
        self.assertEqual(testsuite.tests, 1)

    def test_multiple(self) -> None:
        errors = {"file1": [self.error], "file2": [self.error]}
        testsuite = generate_test_suite(errors)
        self.assertEqual(testsuite.errors, 2)
        self.assertEqual(testsuite.failures, 0)
        self.assertEqual(testsuite.skipped, 0)
        self.assertEqual(testsuite.tests, 2)


class ParseArgumentsTestCase(unittest.TestCase):
    def test_no_arguments(self) -> None:
        with self.assertRaises(SystemExit):
            # Suppress argparse stderr.
            class NullWriter:
                def write(self, s: str) -> None:
                    pass

            sys.stderr = NullWriter()
            parse_arguments()
