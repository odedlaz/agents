import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "skills/external-audit/approve"
HEAD = "a" * 40
URL = "https://github.com/example/repo/pull/123"


class ApproveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="approve-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.script = self.root / "approve"
        shutil.copy2(SCRIPT, self.script)
        self.config = self.root / ".env"
        self.config.write_text("API_KEY=synthetic-legacy\n")
        self.env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ["PATH"],
                        AUDIT_TEST_ROOT=str(self.root), EXTERNAL_AUDIT_REVIEWED_HEAD=HEAD)
        mock = self.root / "gh"
        mock.write_text("""#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root = Path(os.environ['AUDIT_TEST_ROOT'])
with (root / 'tokens.jsonl').open('a') as log:
    log.write(json.dumps(os.environ['GH_TOKEN']) + '\\n')
args = sys.argv[1:]
assert args[args.index('--hostname') + 1] == 'github.com'
if 'POST' in args:
    assert 'repos/example/repo/pulls/123/reviews' in args
    assert 'event=APPROVE' in args
    assert 'commit_id=' + os.environ['EXTERNAL_AUDIT_REVIEWED_HEAD'] in args
    (root / 'posted').touch()
    if os.environ.get('AUDIT_TEST_FAIL_POST'):
        print('API unavailable', file=sys.stderr)
        sys.exit(1)
    print(json.dumps({'reviewer': 'auditor', 'state': 'APPROVED'}))
elif 'user' in args:
    print('auditor')
else:
    print(os.environ.get('AUDIT_TEST_AUTHOR', 'author') + '\\t' +
          os.environ.get('AUDIT_TEST_STATE', 'open') + '\\t' +
          os.environ.get('AUDIT_TEST_HEAD', os.environ['EXTERNAL_AUDIT_REVIEWED_HEAD']))
""")
        mock.chmod(0o755)

    def run_script(self, seed=0):
        return subprocess.run(
            ["/bin/bash", "-c", 'RANDOM=$1; source "$2" "$3"', "approve-test",
             str(seed), str(self.script), URL],
            env=self.env, capture_output=True, text=True,
        )

    def tokens(self):
        path = self.root / "tokens.jsonl"
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def test_keeps_legacy_single_token_support(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tokens(), ["synthetic-legacy"] * 3)
        self.assertNotIn("synthetic-legacy", result.stdout + result.stderr)

    def test_randomly_selects_one_csv_token_for_the_whole_invocation(self):
        self.config.write_text('API_KEY="synthetic-one, synthetic-two ,synthetic-three"\n')
        selected = set()
        for seed in range(8):
            with self.subTest(seed=seed):
                result = self.run_script(seed)
                self.assertEqual(result.returncode, 0, result.stderr)
                tokens = self.tokens()[-3:]
                self.assertEqual(len(set(tokens)), 1)
                self.assertIn(tokens[0], {"synthetic-one", "synthetic-two", "synthetic-three"})
                selected.add(tokens[0])
                self.assertNotIn("synthetic-", result.stdout + result.stderr)
        self.assertEqual(selected, {"synthetic-one", "synthetic-two", "synthetic-three"})

    def test_trims_a_single_token(self):
        self.config.write_text('API_KEY=" synthetic-one "\n')
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.tokens(), ["synthetic-one"] * 3)

    def test_rejects_empty_csv_entries_before_contacting_github(self):
        for value in ["", " ", ",synthetic-one", "synthetic-one,", "synthetic-one,,synthetic-two"]:
            with self.subTest(value=value):
                self.config.write_text('API_KEY="' + value + '"\n')
                result = self.run_script()
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(self.tokens(), [])
                self.assertNotIn("synthetic-", result.stdout + result.stderr)

    def test_ignores_inherited_credentials(self):
        self.config.write_text("# No credentials configured here\n")
        self.env.update(API_KEY="synthetic-inherited", API_KEYS="synthetic-inherited-list")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tokens(), [])

    def test_rejects_self_review_closed_pr_and_changed_head(self):
        self.config.write_text("API_KEY=synthetic-one,synthetic-two\n")
        for key, value in [("AUDIT_TEST_AUTHOR", "auditor"), ("AUDIT_TEST_STATE", "closed"),
                           ("AUDIT_TEST_HEAD", "b" * 40)]:
            with self.subTest(key=key):
                self.env[key] = value
                result = self.run_script()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / "posted").exists())
                self.env.pop(key)

    def test_propagates_publication_failure_without_trying_another_token(self):
        self.config.write_text("API_KEY=synthetic-one,synthetic-two\n")
        self.env["AUDIT_TEST_FAIL_POST"] = "1"
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(len(self.tokens()), 3)
        self.assertIn("API unavailable", result.stderr)

    def test_rejects_missing_dotenv(self):
        self.config.unlink()
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.tokens(), [])


if __name__ == "__main__":
    unittest.main()
