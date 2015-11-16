#! /usr/bin/env python3

"""cppcheck-junit tests."""

import unittest

from cppcheck_junit import parse_cppcheck


class ParseCppcheckTestCase(unittest.TestCase):
    def test_good(self):
        errors = parse_cppcheck('tests/cppcheck-out-good.xml')
        self.assertEqual(errors, {})

    def test_bad(self):
        file = 'bad.cpp'
        errors = parse_cppcheck('tests/cppcheck-out-bad.xml')

        self.assertEqual(errors[file][0].file, file)
        self.assertEqual(errors[file][0].line, 4)
        self.assertEqual(errors[file][0].message,
                         "Variable 'a' is assigned a value that is never used.")

        self.assertEqual(errors[file][1].file, file)
        self.assertEqual(errors[file][1].line, 4)
        self.assertEqual(errors[file][1].message,
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
