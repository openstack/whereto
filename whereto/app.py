# -*- coding: utf-8 -*-

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

from __future__ import print_function

import argparse
import io

from whereto import parser
from whereto import rules


def process_tests(ruleset, tests):
    """Run the tests against the ruleset and return the results.

    The return value is a tuple containing a list of tuples with the
    inputs that did not match the expected value, and a set containing
    the line numbers of the rules that never matched an input test.

    The mismatched tuples contain the test values (line, input,
    expected).

    :param ruleset: The redirect rules.
    :type ruleset: RuleSet

    """
    used = set()
    mismatches = []
    for test in tests:
        try:
            linenum, input, code, expected = test
        except ValueError as e:
            linenum = test[0]
            if len(test) != 4:
                raise ValueError(
                    'Wrong number of arguments in test on line {}: {}'.format(
                        linenum, ' '.join(test[1:]))
                )
            raise RuntimeError('Unable to process test {}: {}'.format(
                test, e))
        match = ruleset.match(input)
        if match is not None:
            if (code, expected) == match[1:]:
                used.add(match[0])
                continue
        mismatches.append(
            (linenum, input, code, expected)
        )
    untested = set(ruleset.all_ids) - used
    return (mismatches, untested)


# This is constructed outside of the main() function to support
# sphinxcontrib.autoprogram in the doc build.
argument_parser = argparse.ArgumentParser()
group = argument_parser.add_mutually_exclusive_group()
group.add_argument(
    '--ignore-untested',
    action='store_false',
    dest='error_untested',
    default=True,
    help='ignore untested rules',
)
group.add_argument(
    '--error-untested',
    action='store_true',
    dest='error_untested',
    help='error if there are untested rules',
)
argument_parser.add_argument(
    '-q', '--quiet',
    action='store_true',
    default=False,
    help='run quietly',
)
argument_parser.add_argument(
    'htaccess_file',
    help='file with rewrite rules',
)
argument_parser.add_argument(
    'test_file',
    help='file with test data',
)


def main():
    args = argument_parser.parse_args()

    ruleset = rules.RuleSet()
    with io.open(args.htaccess_file, 'r', encoding='utf-8') as f:
        for linenum, params in parser.parse_rules(f):
            ruleset.add(linenum, *params)

    with io.open(args.test_file, 'r', encoding='utf-8') as f:
        tests = [
            (linenum,) + tuple(params)
            for linenum, params in parser.parse_rules(f)
        ]

    failures = 0
    mismatches, untested = process_tests(ruleset, tests)
    for test in mismatches:
        failures += 1
        print('No rule matched test on line {}: {}'.format(
            test[0], ' '.join(test[1:]))
        )

    if untested:
        if not args.quiet:
            print('')
        for linenum in sorted(untested):
            if not args.quiet:
                print('Untested rule: {}'.format(ruleset[linenum]))
            if args.error_untested:
                failures += 1

    if failures:
        print('\n{} failures'.format(failures))
        return 1
    return 0
