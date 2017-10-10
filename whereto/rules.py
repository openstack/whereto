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

import logging
import re


LOG = logging.getLogger()


class Rule(object):
    "Base class for rules."

    def __init__(self, linenum, *params):
        self.linenum = linenum
        self._params = params
        if len(params) == 4:
            # redirect code pattern target
            self.code = params[1]
            self.pattern = params[2]
            self.target = params[3]
        elif len(params) == 3:
            if params[1] == '410':
                # The page has been deleted and is not coming back.
                self.code = params[1]
                self.pattern = params[2]
                self.target = None
            else:
                # redirect pattern target
                # (code is implied)
                self.code = '301'
                self.pattern = params[1]
                self.target = params[2]
        else:
            raise ValueError('Could not understand rule {}'.format(params))

    def __str__(self):
        return '[{}] {}'.format(
            self.linenum,
            ' '.join(p for p in self._params if p),
        )

    def match(self, path):
        raise NotImplementedError('Base class does not implement match()')


class Redirect(Rule):
    "A Redirect rule."

    def match(self, path):
        if path == self.pattern:
            return (self.code, self.target)
        return None


class RedirectMatch(Rule):
    "A RedirectMatch rule with a regular expression."

    def __init__(self, linenum, *params):
        super(RedirectMatch, self).__init__(linenum, *params)
        self.regex = re.compile(self.pattern)
        if self.target:
            self.target_repl = self.target.replace('$', '\\')
        else:
            self.target_repl = None

    def match(self, path):
        m = self.regex.search(path)
        if m:
            if self.target_repl:
                return (self.code, self.regex.sub(self.target_repl, path))
            else:
                # A rule that doesn't have a response target, like 410.
                return (self.code, self.target_repl)
        return None


class RuleSet(object):
    "An ordered collection of rules."

    _factories = {
        'redirect': Redirect,
        'redirectmatch': RedirectMatch,
    }

    def __init__(self):
        self._rules = []
        self._by_num = {}

    def add(self, linenum, *params):
        rule_type = params[0].lower()
        rule = self._factories[rule_type](linenum, *params)
        self._rules.append(rule)
        self._by_num[linenum] = rule

    def __getitem__(self, index):
        return self._by_num[index]

    def __iter__(self):
        return iter(self._rules)

    @property
    def all_ids(self):
        return list(self._by_num.keys())

    def match(self, path):
        for rule in self:
            try:
                m = rule.match(path)
            except Exception as e:
                LOG.warning('Failed to evaluate {} against {}: {}'.format(
                    rule, path, e))
            else:
                if m is not None:
                    LOG.debug(
                        'Matched "{}" for path "{}" producing {}'.format(
                            rule, path, m))
                    return (rule.linenum,) + m
