# -*- coding: utf-8 -*-
"""Tests for vcspull svn repos."""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals, with_statement)

import os
import tempfile
import unittest

from vcspull.exc import VCSPullException
from vcspull.repo import create_repo
from vcspull.util import run, which
from .helpers import ConfigTestCase, RepoTestMixin, stdouts


def has_svn():
    try:
        which('svn')
        return True
    except VCSPullException:
        return False


@unittest.skipUnless(has_svn(), "requires SVN")
class RepoSVN(RepoTestMixin, ConfigTestCase, unittest.TestCase):

    @stdouts
    def test_repo_svn(self, *args):
        repo_dir = os.path.join(self.TMP_DIR, '.repo_dir')
        repo_name = 'my_svn_project'

        svn_repo = create_repo(**{
            'url': 'svn+file://' + os.path.join(repo_dir, repo_name),
            'parent_dir': self.TMP_DIR,
            'name': repo_name
        })

        svn_checkout_dest = os.path.join(self.TMP_DIR, svn_repo['name'])

        os.mkdir(repo_dir)

        run(['svnadmin', 'create', svn_repo['name']], cwd=repo_dir)

        svn_repo.obtain()

        self.assertTrue(os.path.exists(svn_checkout_dest))

        tempFile = tempfile.NamedTemporaryFile(dir=svn_checkout_dest)

        run(['svn', 'add', '--non-interactive', tempFile.name],
            cwd=svn_checkout_dest)
        run(
            ['svn', 'commit', '-m', 'a test file for %s' % svn_repo['name']],
            cwd=svn_checkout_dest
        )
        self.assertEqual(svn_repo.get_revision(), 0)

        self.assertEqual(
            os.path.join(svn_checkout_dest, tempFile.name),
            tempFile.name
        )
        self.assertEqual(svn_repo.get_revision(tempFile.name), 1)