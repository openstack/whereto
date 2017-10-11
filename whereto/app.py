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
import logging
import sys

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
        if match[-1] is None:
            # a redirect that doesn't point to a path, like a 410
            break
        # Look again in case we have multiple matches and a cycle.
        match = ruleset.match(match[-1])
    return matches


def process_tests(ruleset, tests, max_hops):
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
    too_many_hops = []
    for test in tests:
        matches = _find_matches(ruleset, test)
        if not matches:
            # No rules matched at all. If the test was expecting
            # that don't record it as a failure.
            if test[2] == '200':
                used.add(test[0])
            else:
                mismatches.append((test, []))
        else:
            code, expected = test[-2:]
            if (code, expected) != matches[0][1:]:
                # At least one rule matched, but the first rule to
                # match gave us an unexpected result to count it as a
                # failure.
                mismatches.append((test, matches))
            elif len(matches) == 1:
                # One rule matched and it matched as expected, so mark
                # it as used and go on to the next test.
                used.add(matches[0][0])
            else:
                # Multiple rules matched. We only have a cycle if the
                # first and last rule are the same. Otherwise it's a
                # multi-step redirect, which is OK and we can just
                # recognize that the first rule was tested properly.
                if matches[0] == matches[-1]:
                    cycles.append((test, matches))
                elif max_hops and len(matches) > max_hops:
                    too_many_hops.append((test, matches))
                else:
                    used.add(matches[0][0])
    untested = set(ruleset.all_ids) - used
    return (mismatches, cycles, too_many_hops, untested)


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
    '-m', '--max-hops',
    type=int,
    default=0,
    help='how many hops are allowed',
)
argument_parser.add_argument(
    '-v', '--verbose',
    dest='verbosity',
    default=[1],
    action='append_const',
    const=1,
    help='increase the verbosity by one level',
)
argument_parser.add_argument(
    '-q', '--quiet',
    action='store_const',
    dest='verbosity',
    const=[],
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


def show_test_and_matches(msg, test, matches):
    logging.error(
        '{} on line {}: {} should produce {} {}'.format(
            msg, test[0], test[1], test[2], test[3] or '')
    )
    path = test[1]
    for linenum, code, new_path in matches:
        logging.error('   {} -> {} {} [line {}]'.format(
            path, code, new_path, linenum))


def main():
    args = argument_parser.parse_args()

    verbosity = sum(args.verbosity)
    if verbosity < 1:
        log_level = logging.WARNING
    elif verbosity == 1:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG

    logging.basicConfig(
        level=log_level,
        format='whereto %(levelname)s: %(message)s',
        stream=sys.stdout,
    )
    log = logging.getLogger()

    ruleset = rules.RuleSet()

    log.debug('reading redirects from {}'.format(args.htaccess_file))
    with io.open(args.htaccess_file, 'r', encoding='utf-8') as f:
        for linenum, params in parser.parse_rules(f):
            ruleset.add(linenum, *params)

    log.debug('reading tests from {}'.format(args.htaccess_file))
    with io.open(args.test_file, 'r', encoding='utf-8') as f:
        tests = [
            (linenum,) + tuple(params)
            for linenum, params in parser.parse_tests(f)
        ]

    failures = 0
    mismatches, cycles, too_many_hops, untested = process_tests(
        ruleset, tests, args.max_hops)

    for test, matches in mismatches:
        failures += 1
        if matches:
            show_test_and_matches(
                'Unexpected rule matched test',
                test,
                matches,
            )
        else:
            show_test_and_matches(
                'No rule matched test',
                test,
                [],
            )

    for test, matches in cycles:
        failures += 1
        show_test_and_matches(
            'Cycle found from rule',
            test,
            matches,
        )

    for test, matches in too_many_hops:
        failures += 1
        show_test_and_matches(
            'Excessive redirects found from rule',
            test,
            matches,
        )

    if untested:
        log.debug('')
        for linenum in sorted(untested):
            if verbosity:
                logging.error('Untested rule: {}'.format(ruleset[linenum]))
            if args.error_untested:
                failures += 1

    if failures:
        logging.error('{} failures'.format(failures))
        return 1
    return 0
