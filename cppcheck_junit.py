#!/usr/bin/env python3

"""Converts Cppcheck XML version 2 output to JUnit XML format."""

import argparse
import collections
from datetime import datetime
import os
from socket import gethostname
import sys
from typing import Dict, List
from xml.etree import ElementTree

from exitstatus import ExitStatus


class CppcheckLocation:
    def __init__(self, file: str, line: int, column: int, info: str) -> None:
        """Constructor.
        Args:
            file: Error location file.
            line: Error location line.
            column: Error location column.
            info: Error location info.
        """

        self.file = file
        self.line = line
        self.column = column
        self.info = info


class CppcheckError:
    def __init__(
        self,
        file: str,
        locations: [CppcheckLocation],
        message: str,
        severity: str,
        error_id: str,
        verbose: str,
    ) -> None:
        """Constructor.

        Args:
            file: File error originated on.
            locations: Error locations.
            message: Error message.
            severity: Severity of the error.
            error_id: Unique identifier for the error.
            verbose: Verbose error message.
        """
        self.file = file
        self.locations = locations
        self.message = message
        self.severity = severity
        self.error_id = error_id
        self.verbose = verbose


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
        const=0,
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

    if root.get("version") is None or int(root.get("version")) != 2:
        raise ValueError("Parser only supports Cppcheck XML version 2.  Use --xml-version=2.")

    error_root = root.find("errors")

    errors = collections.defaultdict(list)
    for error_element in error_root:
        file = error_element.get("file0", "")
        locations = []
        for location in error_element.findall("location"):
            if not file:
                file = location.get("file", "")
            locations.append(
                CppcheckLocation(
                    location.get("file"),
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


def generate_test_suite(errors: Dict[str, List[CppcheckError]]) -> ElementTree.ElementTree:
    """Converts parsed Cppcheck errors into JUnit XML tree.

    Args:
        errors: Parsed cppcheck errors.

    Returns:
        XML test suite.
    """
    test_suite = ElementTree.Element("testsuite")
    test_suite.attrib["name"] = "Cppcheck errors"
    test_suite.attrib["timestamp"] = datetime.isoformat(datetime.now())
    test_suite.attrib["hostname"] = gethostname()
    test_suite.attrib["tests"] = str(len(errors))
    test_suite.attrib["failures"] = str(0)
    test_suite.attrib["errors"] = str(len(errors))
    test_suite.attrib["time"] = str(1)

    for file_name, errors in errors.items():
        test_case = ElementTree.SubElement(
            test_suite,
            "testcase",
            name=os.path.relpath(file_name) if file_name else "Cppcheck error",
            classname="Cppcheck error",
            time=str(1),
        )
        for error in errors:
            error_element = ElementTree.SubElement(
                test_case,
                "error",
                type=error.severity,
                file=os.path.relpath(error.file) if error.file else "",
                message=f"{error.message}",
            )
            if len(error.locations) == 0:
                error_element.text = error.verbose
            elif len(error.locations) == 1 and error.locations[0].info == "":
                location = error.locations[0]
                file = os.path.relpath(location.file) if location.file else ""
                error_element.text = f"{file}:{location.line}:{location.column}: {error.verbose}"
            else:
                error_element.text = error.verbose
                for location in error.locations:
                    file = os.path.relpath(location.file) if location.file else ""
                    error_element.text += (
                        f"\n{file}:{location.line}:{location.column}: {location.info}"
                    )

    return ElementTree.ElementTree(test_suite)


def generate_single_success_test_suite() -> ElementTree.ElementTree:
    """Generates a single successful JUnit XML testcase."""
    test_suite = ElementTree.Element("testsuite")
    test_suite.attrib["name"] = "Cppcheck errors"
    test_suite.attrib["timestamp"] = datetime.isoformat(datetime.now())
    test_suite.attrib["hostname"] = gethostname()
    test_suite.attrib["tests"] = str(1)
    test_suite.attrib["failures"] = str(0)
    test_suite.attrib["errors"] = str(0)
    test_suite.attrib["time"] = str(1)
    ElementTree.SubElement(
        test_suite, "testcase", name="Cppcheck success", classname="Cppcheck success", time=str(1)
    )
    return ElementTree.ElementTree(test_suite)


def main() -> ExitStatus:  # pragma: no cover
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

    if len(errors) > 0:
        tree = generate_test_suite(errors)
        tree.write(args.output_file, encoding="utf-8", xml_declaration=True)
        return args.error_exitcode
    else:
        tree = generate_single_success_test_suite()
        tree.write(args.output_file, encoding="utf-8", xml_declaration=True)
        return ExitStatus.success


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
