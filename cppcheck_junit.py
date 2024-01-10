#!/usr/bin/env python3

"""Converts Cppcheck XML version 2 output to JUnit XML format."""

import argparse
import collections
from dataclasses import dataclass
from datetime import datetime
from socket import gethostname
import sys
from typing import Dict, List
from xml.etree import ElementTree

from exitstatus import ExitStatus
from junitparser import Error, JUnitXml, TestCase, TestSuite


@dataclass
class CppcheckLocation:
    """
    file: Error location file.
    line: Error location line.
    column: Error location column.
    info: Error location info.
    """

    file: str
    line: int
    column: int
    info: str


@dataclass
class CppcheckError:
    """
    file: File error originated on.
    locations: Error locations.
    message: Error message.
    severity: Severity of the error.
    error_id: Unique identifier for the error.
    verbose: Verbose error message.
    """

    file: str
    locations: List[CppcheckLocation]
    message: str
    severity: str
    error_id: str
    verbose: str


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Converts Cppcheck XML version 2 to JUnit XML format.\n"
        "Usage:\n"
        "\t$ cppcheck --xml-version=2 --enable=all . 2> cppcheck-result.xml\n"
        "\t$ cppcheck_junit cppcheck-result.xml cppcheck-junit.xml\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("input_file", type=str, help="Cppcheck XML version 2 stderr file.")
    parser.add_argument("output_file", type=str, help="JUnit XML output file.")
    parser.add_argument(
        "error_exitcode",
        type=int,
        nargs="?",
        default=ExitStatus.success,
        help="If errors are found, "
        f"integer <n> is returned instead of default {ExitStatus.success}.",
    )
    return parser.parse_args()


def parse_cppcheck(file_name: str) -> Dict[str, List[CppcheckError]]:
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
    root: ElementTree.Element = ElementTree.parse(file_name).getroot()

    if int(root.get("version", "0")) != 2:
        raise ValueError("Parser only supports Cppcheck XML version 2.  Use --xml-version=2.")

    error_root = root.find("errors")
    errors = collections.defaultdict(list)
    if error_root is not None:
        for error_element in error_root:
            file = error_element.get("file0", "")
            locations = []
            for location in error_element.findall("location"):
                if not file:
                    file = location.get("file", "")
                locations.append(
                    CppcheckLocation(
                        location.get("file", ""),
                        int(location.get("line", 0)),
                        int(location.get("column", 0)),
                        location.get("info", ""),
                    )
                )

            error = CppcheckError(
                file=file,
                locations=locations,
                message=error_element.get("msg", ""),
                severity=error_element.get("severity", ""),
                error_id=error_element.get("id", ""),
                verbose=error_element.get("verbose", ""),
            )
            errors[error.file].append(error)

    return errors


def generate_test_error(error: CppcheckError) -> Error:
    """Converts parsed Cppcheck error into Error.

    Args:
        error: Cppcheck error

    Returns:
        Error
    """

    jerror = Error(error.message, f"{error.severity}:{error.error_id}")
    if len(error.locations) == 0:
        jerror.text = error.verbose
    elif len(error.locations) == 1 and error.locations[0].info == "":
        location = error.locations[0]
        jerror.text = f"{location.file}:{location.line}:{location.column}: {error.verbose}"
    else:
        jerror.text = error.verbose
        for location in error.locations:
            jerror.text += f"\n{location.file}:{location.line}:{location.column}: {location.info}"

    return jerror


def generate_test_case(name: str, class_name: str, errors: List[CppcheckError]) -> TestCase:
    """Converts parsed Cppcheck errors into TestCase.

    Args:
        name: Name for the test case
        class_name: Class for the test case
        errors: Parsed cppcheck errors.

    Returns:
        TestCase
    """

    test_case = TestCase(name if name else "Cppcheck", class_name, 1)
    jerrors = []
    for error in errors:
        jerrors.append(generate_test_error(error))
    test_case.result = jerrors

    return test_case


def generate_test_suite(errors: Dict[str, List[CppcheckError]]) -> TestSuite:
    """Converts parsed Cppcheck errors into TestSuite.

    Args:
        errors: Parsed cppcheck errors.

    Returns:
        TestSuite
    """
    test_suite = TestSuite("Cppcheck")
    test_suite.timestamp = datetime.isoformat(datetime.now())
    test_suite.hostname = gethostname()

    if len(errors) == 0:
        test_suite.add_testcase(generate_test_case("", "Cppcheck success", []))

    for name, cerrors in errors.items():
        test_suite.add_testcase(generate_test_case(name, "Cppcheck error", cerrors))

    return test_suite


def main() -> int:  # pragma: no cover
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
        print(f"{args.input_file} is a malformed XML file. Did you use --xml-version=2?\n{e}")
        return ExitStatus.failure

    tree = JUnitXml("Cppcheck")
    tree.add_testsuite(generate_test_suite(errors))
    tree.write(args.output_file)
    return int(args.error_exitcode) if len(errors) > 0 else ExitStatus.success


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
