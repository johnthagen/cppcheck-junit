#! /usr/bin/env python3

"""cppcheck-junit tests."""

import unittest
from xml.etree import ElementTree

from cppcheck_junit import parse_cppcheck


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


if __name__ == '__main__':
    unittest.main()
