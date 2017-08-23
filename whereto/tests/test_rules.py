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
        )
