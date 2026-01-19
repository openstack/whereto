# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections.abc import Iterable, Iterator
import shlex


def parse_rules(fd: Iterable[str]) -> Iterator[tuple[int, list[str]]]:
    """Parse an open file containing redirect rules.

    Generates a sequence of tuples containing line numbers and the
    parsed lines.

    Blank lines and lines starting with # are skipped.

    :param fd: Open file handle or other data source supporting
               iteration over lines, producing unicode strings.
    :type fd: io.BufferedReader
    """
    for num, line in enumerate(fd, 1):
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            continue
        yield (num, shlex.split(line))


def parse_tests(
    fd: Iterable[str],
) -> Iterator[tuple[int, list[str | None]]]:
    """Parse an open file containing tests for redirect rules.

    Generates a sequence of tuples containing line numbers and the
    parsed lines.

    Blank lines and lines starting with # are skipped.

    :param fd: Open file handle or other data source supporting
               iteration over lines, producing unicode strings.
    :type fd: io.BufferedReader
    """
    # A test line looks like a rule line except that it might not have
    # the same number of parts.
    for linenum, test in parse_rules(fd):
        padded_test: list[str | None] = list(test)
        if len(padded_test) < 3:
            padded_test = (padded_test + [None, None, None])[:3]
        yield (linenum, padded_test)
