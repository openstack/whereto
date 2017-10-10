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

from whereto import rules
from whereto.tests import base


class TestRedirect(base.TestCase):

    def setUp(self):
        super(TestRedirect, self).setUp()
        self.rule = rules.Redirect(
            1,
            'redirect', '301', '/path', '/new/path',
        )

    def test_match(self):
        self.assertEqual(
            ('301', '/new/path'),
            self.rule.match('/path'),
        )

    def test_no_match(self):
        self.assertIsNone(
            self.rule.match('/different/path'),
        )

    def test_implied_code(self):
        rule = rules.Redirect(
            1,
            'redirect', '/the/path', '/new/path',
        )
        self.assertEqual(
            '301',
            rule.code,
        )

    def test_str(self):
        self.assertEqual(
            '[1] redirect 301 /path /new/path',
            str(self.rule),
        )

    def test_too_few_args(self):
        self.assertRaises(
            ValueError,
            rules.Redirect,
            (1, 'redirect', '/the/path'),
        )

    def test_too_many_args(self):
        self.assertRaises(
            ValueError,
            rules.Redirect,
            (1, 'redirect', '301', '/the/path', '/new/path', 'extra-value'),
        )

    def test_410(self):
        rule = rules.Redirect(
            1,
            'redirect', '410', '/the/path', None,
        )
        self.assertEqual(
            '410',
            rule.code,
        )
        self.assertIsNone(
            rule.target,
        )
        self.assertEqual(
            ('410', None),
            rule.match('/the/path'),
        )


class TestRedirectMatch(base.TestCase):

    def test_match(self):
        rule = rules.RedirectMatch(
            1,
            'redirectmatch', '301', '^/user/.*$', '/pike/user/',
        )
        self.assertEqual(
            ('301', '/pike/user/'),
            rule.match('/user/'),
        )

    def test_match_with_group(self):
        rule = rules.RedirectMatch(
            1,
            'redirectmatch', '301', '^/user/(.*)$', '/pike/user/$1',
        )
        self.assertEqual(
            ('301', '/pike/user/foo'),
            rule.match('/user/foo'),
        )

    def test_no_match(self):
        rule = rules.RedirectMatch(
            1,
            'redirectmatch', '301', '^/user/.*$', '/pike/user/',
        )
        self.assertIsNone(
            rule.match('/different/path'),
        )

    def test_implied_code(self):
        rule = rules.RedirectMatch(
            1,
            'redirectmatch', '^/user/.*$', '/pike/user/',
        )
        self.assertEqual(
            '301',
            rule.code,
        )

    def test_str(self):
        rule = rules.RedirectMatch(
            1,
            'redirectmatch', '301', '^/user/.*$', '/pike/user/',
        )
        self.assertEqual(
            '[1] redirectmatch 301 ^/user/.*$ /pike/user/',
            str(rule),
        )

    def test_too_few_args(self):
        self.assertRaises(
            ValueError,
            rules.RedirectMatch,
            (1, 'redirectmatch', '/the/path'),
        )

    def test_too_many_args(self):
        self.assertRaises(
            ValueError,
            rules.RedirectMatch,
            (1, 'redirectmatch', '301', '/the/path', '/new/path',
             'extra-value'),
        )

    def test_410(self):
        rule = rules.RedirectMatch(
            1,
            'redirect', '410', '/the/path', None,
        )
        self.assertEqual(
            '410',
            rule.code,
        )
        self.assertIsNone(
            rule.target,
        )
        self.assertEqual(
            ('410', None),
            rule.match('/the/path'),
        )


class TestRuleSet(base.TestCase):

    def setUp(self):
        super(TestRuleSet, self).setUp()
        self.ruleset = rules.RuleSet()

    def test_add_redirect(self):
        self.ruleset.add(
            1,
            'redirect', '301', '/path', '/new/path',
        )
        self.assertEqual(1, len(self.ruleset._rules))
        self.assertIsInstance(self.ruleset._rules[0], rules.Redirect)

    def test_add_redirectmatch(self):
        self.ruleset.add(
            1,
            'redirectmatch', '301', '/path', '/new/path',
        )
        self.assertEqual(1, len(self.ruleset._rules))
        self.assertIsInstance(self.ruleset._rules[0], rules.RedirectMatch)

    def test_all_ids(self):
        self.ruleset.add(
            1,
            'redirect', '301', '/path', '/new/path',
        )
        self.assertEqual([1], self.ruleset.all_ids)
        self.ruleset.add(
            2,
            'redirect', '301', '/path', '/other/path',
        )
        self.assertEqual([1, 2], self.ruleset.all_ids)

    def test_match_one(self):
        self.ruleset.add(
            1,
            'redirect', '301', '/path', '/new/path',
        )
        self.assertEqual(
            (1, '301', '/new/path'),
            self.ruleset.match('/path'),
        )

    def test_match_multiple(self):
        self.ruleset.add(
            1,
            'redirect', '301', '/path', '/new/path',
        )
        self.ruleset.add(
            2,
            'redirect', '301', '/path', '/other/path',
        )
        self.assertEqual(
            (1, '301', '/new/path'),
            self.ruleset.match('/path'),
        )
