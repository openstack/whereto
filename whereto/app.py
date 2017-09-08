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


def _find_matches(ruleset, test):
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
    seen = set()
    matches = []
    match = ruleset.match(input)
    while match is not None and len(matches) < 5:
        matches.append(match)
        if match[0] in seen:
            # cycle, stop
            break
        seen.add(match[0])
        # Look again in case we have multiple matches and a cycle.
        match = ruleset.match(match[-1])
    return matches


def process_tests(ruleset, tests):
    """Run the tests against the ruleset and return the results.

    The return value is a tuple containing a list of tuples with the
    inputs that did not match the expected value, a list of tuples
    with inputs and rules the result in redirect cycles, and a set
    containing the line numbers of the rules that never matched an
    input test.

    The mismatched tuples contain the test values (line, input,
    expected).

    :param ruleset: The redirect rules.
    :type ruleset: RuleSet

    """
    used = set()
    mismatches = []
    cycles = []
    for test in tests:
        matches = _find_matches(ruleset, test)
        if not matches:
            mismatches.append(test)
        elif len(matches) == 1:
            code, expected = test[-2:]
            if (code, expected) == matches[0][1:]:
                used.add(matches[0][0])
                continue
        else:
            # We only have a cycle if the first and last rule
            # match. Otherwise it's a multi-step redirect, which is OK
            # and we can just recognize that the first rule was tested
            # properly.
            if matches[0] == matches[-1]:
                cycles.append((test, matches))
            else:
                used.add(matches[0][0])
    untested = set(ruleset.all_ids) - used
    return (mismatches, cycles, untested)


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
    mismatches, cycles, untested = process_tests(ruleset, tests)
    for test in mismatches:
        failures += 1
        print('No rule matched test on line {}: {}'.format(
            test[0], ' '.join(test[1:]))
        )

    for test, matches in cycles:
        failures += 1
        print('Cycle found from rule on line {}: {}'.format(
            test[0], ' '.join(test[1:]))
        )
        path = test[1]
        for linenum, code, new_path in matches:
            print('  {} -> {} ({})'.format(
                path, new_path, code))

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
