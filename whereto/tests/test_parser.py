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

import io
import textwrap

from whereto import parser
from whereto.tests import base


class TestParseRules(base.TestCase):

    def parse(self, text):
        input = io.StringIO(textwrap.dedent(text))
        return list(parser.parse_rules(input))

    def test_skip_comments(self):
        input = u"""
        #
        """
        self.assertEqual(
            [],
            self.parse(input),
        )

    def test_skip_blank_lines(self):
        input = u"""

        """
        self.assertEqual(
            [],
            self.parse(input),
        )

    def test_no_quotes(self):
        input = u"""
        redirect /path /new/path
        """
        self.assertEqual(
            [(2, ['redirect', '/path', '/new/path'])],
            self.parse(input),
        )

    def test_strip_quotes(self):
        input = u"""
        redirectmatch 301 "^/releases.*$" http://releases.openstack.org$1
        """
        self.assertEqual(
            [(2, ['redirectmatch', '301', '^/releases.*$',
                  'http://releases.openstack.org$1'])],
            self.parse(input),
        )


class TestParseTests(base.TestCase):

    def parse(self, text):
        input = io.StringIO(textwrap.dedent(text))
        return list(parser.parse_tests(input))

    def test_skip_comments(self):
        input = u"""
        #
        """
        self.assertEqual(
            [],
            self.parse(input),
        )

    def test_skip_blank_lines(self):
        input = u"""

        """
        self.assertEqual(
            [],
            self.parse(input),
        )

    def test_no_quotes(self):
        input = u"""
        /path 301 /new/path
        """
        self.assertEqual(
            [(2, ['/path', '301', '/new/path'])],
            self.parse(input),
        )

    def test_strip_quotes(self):
        input = u"""
        /releases/foo 301 http://releases.openstack.org/foo
        """
        self.assertEqual(
            [(2, ['/releases/foo', '301',
                  'http://releases.openstack.org/foo'])],
            self.parse(input),
        )

    def test_410_rule(self):
        input = u"""
        /releases 410
        """
        self.assertEqual(
            [(2, ['/releases', '410', None])],
            self.parse(input),
        )

    def test_200_rule(self):
        input = u"""
        /releases 200
        """
        self.assertEqual(
            [(2, ['/releases', '200', None])],
            self.parse(input),
        )
