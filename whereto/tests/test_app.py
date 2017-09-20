# -*- coding: utf-8 -*-

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

from whereto import app
from whereto import rules
from whereto.tests import base


class TestProcessTests(base.TestCase):

    def setUp(self):
        super(TestProcessTests, self).setUp()
        self.ruleset = rules.RuleSet()
        self.ruleset.add(
            1,
            'redirect', '301', '/path', '/new/path',
        )

    def test_zero_matches(self):
        actual = app.process_tests(
            self.ruleset,
            [(1, '/alternate/path', '301', '/new/path')],
            0,
        )
        expected = (
            [((1, '/alternate/path', '301', '/new/path'), [])],
            [],
            [],
            {1},
        )
        self.assertEqual(expected, actual)

    def test_one_match(self):
        actual = app.process_tests(
            self.ruleset,
            [(1, '/path', '301', '/new/path')],
            0,
        )
        expected = ([], [], [], set())
        self.assertEqual(expected, actual)

    def test_two_matches(self):
        self.ruleset.add(
            2,
            'redirect', '301', '/path', '/duplicate/redirect',
        )
        actual = app.process_tests(
            self.ruleset,
            [(1, '/path', '301', '/new/path')],
            0,
        )
        expected = (
            [],
            [],
            [],
            {2},
        )
        self.assertEqual(expected, actual)

    def test_mismatch(self):
        ruleset = rules.RuleSet()
        ruleset.add(
            1,
            'redirect', '301', '/path', '/new/path/',
        )
        actual = app.process_tests(
            ruleset,
            [(1, '/path', '301', '/new/path')],
            0,
        )
        expected = (
            [((1, '/path', '301', '/new/path'), [(1, '301', '/new/path/')])],
            [],
            [],
            {1},
        )
        self.assertEqual(expected, actual)

    def test_cycle(self):
        self.ruleset.add(
            2,
            'redirect', '301', '/new/path', '/path',
        )
        actual = app.process_tests(
            self.ruleset,
            [(1, '/path', '301', '/new/path')],
            0,
        )
        expected = (
            [],
            [((1, '/path', '301', '/new/path'),
              [(1, '301', '/new/path'),
               (2, '301', '/path'),
               (1, '301', '/new/path')])],
            [],
            {1, 2},
        )
        self.assertEqual(expected, actual)

    def test_max_hops(self):
        self.ruleset.add(
            2,
            'redirect', '301', '/new/path', '/second/path',
        )
        self.ruleset.add(
            3,
            'redirect', '301', '/second/path', '/third/path',
        )
        actual = app.process_tests(
            self.ruleset,
            [(1, '/path', '301', '/new/path')],
            1,
        )
        expected = (
            [],
            [],
            [((1, '/path', '301', '/new/path'),
              [(1, '301', '/new/path'),
               (2, '301', '/second/path'),
               (3, '301', '/third/path')])],
            {1, 2, 3},
        )
        self.assertEqual(expected, actual)
