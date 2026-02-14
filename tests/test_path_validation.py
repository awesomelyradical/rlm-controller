#!/usr/bin/env python3
"""Tests for path validation and ReDoS protection across scripts."""
import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPTS_DIR = os.path.join(os.path.dirname(__file__), '..', 'scripts')


class TestPathTraversal(unittest.TestCase):
    """Verify that path traversal attempts are rejected."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ctx_file = os.path.join(self.tmpdir, 'sample.txt')
        with open(self.ctx_file, 'w') as f:
            f.write('sample content for testing\n')

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_ctx_store_rejects_dot_dot_infile(self):
        """rlm_ctx.py store should reject --infile with '..' path segments."""
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_ctx.py'),
            'store', '--infile', '../../../etc/passwd',
            '--ctx-dir', self.tmpdir,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('path traversal', result.stderr)

    def test_ctx_store_rejects_dot_dot_ctxdir(self):
        """rlm_ctx.py store should reject --ctx-dir with '..' path segments."""
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_ctx.py'),
            'store', '--infile', self.ctx_file,
            '--ctx-dir', os.path.join(self.tmpdir, '..', '..', 'etc'),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('path traversal', result.stderr)

    def test_ctx_search_rejects_dot_dot(self):
        """rlm_ctx.py search should reject --ctx with '..' path segments."""
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_ctx.py'),
            'search', '--ctx', '../../../etc/passwd', '--pattern', 'root',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('path traversal', result.stderr)

    def test_plan_rejects_dot_dot(self):
        """rlm_plan.py should reject --ctx with '..' path segments."""
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_plan.py'),
            '--ctx', '../../../etc/passwd', '--goal', 'test',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('path traversal', result.stderr)


class TestSymlinkProtection(unittest.TestCase):
    """Verify that symlinks pointing outside expected location are rejected."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_ctx_meta_rejects_symlink(self):
        """rlm_ctx.py meta should reject a symlink pointing to a different location."""
        target = os.path.join(self.tmpdir, 'real.txt')
        with open(target, 'w') as f:
            f.write('real content')
        link = os.path.join(self.tmpdir, 'link.txt')
        os.symlink(target, link)

        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_ctx.py'),
            'meta', '--ctx', link,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('symlink', result.stderr)


class TestReDoSProtection(unittest.TestCase):
    """Verify that regex search is protected against catastrophic backtracking."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.ctx_file = os.path.join(self.tmpdir, 'redos_test.txt')
        # Create content that triggers ReDoS with evil pattern
        with open(self.ctx_file, 'w') as f:
            f.write('a' * 30)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_invalid_regex_rejected(self):
        """rlm_ctx.py search should reject invalid regex patterns."""
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_ctx.py'),
            'search', '--ctx', self.ctx_file, '--pattern', '[invalid',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('invalid regex', result.stderr)

    def test_redos_pattern_times_out(self):
        """rlm_ctx.py search should time out on ReDoS patterns instead of hanging."""
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_ctx.py'),
            'search', '--ctx', self.ctx_file, '--pattern', '(a+)+b',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        # Should exit with error (timeout) rather than hanging
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('timed out', result.stderr)

    def test_normal_regex_works(self):
        """rlm_ctx.py search should work normally with safe patterns."""
        ctx_file = os.path.join(self.tmpdir, 'normal.txt')
        with open(ctx_file, 'w') as f:
            f.write('hello world test content')
        cmd = [
            sys.executable,
            os.path.join(SCRIPTS_DIR, 'rlm_ctx.py'),
            'search', '--ctx', ctx_file, '--pattern', 'hello',
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0)
        matches = json.loads(result.stdout)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['match'], 'hello')


if __name__ == '__main__':
    unittest.main()
