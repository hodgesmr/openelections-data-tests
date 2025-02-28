import csv
import glob
import logging
import os
import unittest
from typing import Iterator

from data_tests.duplicate_entries import DuplicateEntries
from data_tests.inconsistencies import VoteBreakdownTotals
from data_tests.missing_values import MissingValue


def get_csv_files(root_path: str) -> Iterator[str]:
    for file in glob.glob(os.path.join(root_path, "[0-9]" * 4, "**", "*"), recursive=True):
        if file.lower().endswith(".csv"):
            yield file


class TestCase(unittest.TestCase):
    log_file = None
    max_examples = -1
    root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if TestCase.log_file is None:
            self.__logger = None
        else:
            self.__logger = TestCase.__get_logger(type(self).__name__, TestCase.log_file)

    def _assertTrue(self, result: bool, description: str, short_message: str, full_message: str):
        if not result:
            self._log_failure(description, full_message)
        self.assertTrue(result, short_message)

    def _log_failure(self, description: str, message: str):
        if self.__logger is not None:
            self.__logger.debug("======================================================================")
            self.__logger.debug(f"FAIL: {description}")
            self.__logger.debug("----------------------------------------------------------------------")
            self.__logger.debug(f"{message}\n")

    @staticmethod
    def __get_logger(name: str, log_file: str) -> logging.Logger:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(logging.Formatter("%(message)s"))

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

        return logger


class DuplicateEntriesTest(TestCase):
    def test_duplicate_entries(self):
        for csv_file in get_csv_files(TestCase.root_path):
            short_path = os.path.relpath(csv_file, start=TestCase.root_path)

            with self.subTest(msg=f"{short_path}"):
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    data_test = DuplicateEntries(headers)
                    data_test.test(headers)
                    for row in reader:
                        data_test.test(row)

                short_message = data_test.get_failure_message(max_examples=TestCase.max_examples)
                full_message = data_test.get_failure_message()
                self._assertTrue(data_test.passed, f"{self} [{short_path}]", short_message, full_message)


class MissingValuesTest(TestCase):
    def test_missing_values(self):
        for csv_file in get_csv_files(TestCase.root_path):
            short_path = os.path.relpath(csv_file, start=TestCase.root_path)

            with self.subTest(msg=f"{short_path}"):
                tests = []
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    tests.append(MissingValue("county", headers))
                    tests.append(MissingValue("precinct", headers))
                    tests.append(MissingValue("office", headers))

                    for test in tests:
                        test.test(headers)

                    for row in reader:
                        for test in tests:
                            test.test(row)

                passed = True
                short_message = ""
                full_message = ""
                is_first_message = True
                for test in tests:
                    if not test.passed:
                        passed = False
                        short_message += f"\n\n* {test.get_failure_message(max_examples=TestCase.max_examples)}"
                        if not is_first_message:
                            full_message += "\n\n"
                        full_message += f"* {test.get_failure_message()}"
                        is_first_message = False

                self._assertTrue(passed, f"{self} [{short_path}]", short_message, full_message)


class VoteBreakdownTotalsTest(TestCase):
    def test_vote_method_totals(self):
        for csv_file in get_csv_files(TestCase.root_path):
            short_path = os.path.relpath(csv_file, start=TestCase.root_path)

            with self.subTest(msg=f"{short_path}"):
                with open(csv_file, "r") as csv_data:
                    reader = csv.reader(csv_data)
                    headers = next(reader)

                    data_test = VoteBreakdownTotals(headers)
                    data_test.test(headers)
                    for row in reader:
                        data_test.test(row)

                short_message = data_test.get_failure_message(max_examples=TestCase.max_examples)
                full_message = data_test.get_failure_message()
                self._assertTrue(data_test.passed, f"{self} [{short_path}]", short_message, full_message)
