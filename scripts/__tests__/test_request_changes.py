import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[2] / "skills/external-audit/request-changes"
HEAD = "a" * 40
URL = "https://github.com/example/repo/pull/123"


class RequestChangesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="request-changes-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / ".env").write_text("API_KEY=synthetic-review-token\n")
        self.env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ["PATH"],
                        AUDIT_TEST_ROOT=str(self.root), AUDIT_TEST_HEAD=HEAD)
        self.env.pop("EXTERNAL_AUDIT_REVIEWED_HEAD", None)
        mock = self.root / "gh"
        mock.write_text("""#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root = Path(os.environ['AUDIT_TEST_ROOT'])
assert os.environ['GH_TOKEN'] == 'synthetic-review-token'
args = sys.argv[1:]
if 'POST' in args:
    assert 'repos/example/repo/pulls/123/reviews' in args
    assert args[args.index('--hostname') + 1] == 'github.com'
    assert args[args.index('--input') + 1] == '-'
    payload = json.load(sys.stdin)
    (root / 'posted.json').write_text(json.dumps(payload))
    if os.environ.get('AUDIT_TEST_FAIL_POST'):
        print('API unavailable', file=sys.stderr)
        sys.exit(1)
    print(json.dumps({'url': 'https://github.com/example/repo/pull/123#pullrequestreview-1',
                      'reviewer': 'auditor', 'state': 'CHANGES_REQUESTED', 'commit_id': payload['commit_id']}))
elif 'user' in args:
    print('auditor')
else:
    print(os.environ.get('AUDIT_TEST_AUTHOR', 'author') + '\t' +
          os.environ.get('AUDIT_TEST_STATE', 'open') + '\t' + os.environ['AUDIT_TEST_HEAD'])
""")
        mock.chmod(0o755)
        self.payload = {"commit_id": HEAD, "body": "Please address the inline findings.",
                        "comments": [{"path": "src/parse.ts", "line": 42, "side": "RIGHT",
                                      "body": "`null-input` Major: reject null before parsing.\nPreserve valid input."},
                                     {"path": "src/cache.ts", "line": 5, "side": "LEFT",
                                      "body": "`stale-entry` Major: invalidate stale entries."}]}

    def run_script(self, payload=None, stdin=False, url=URL, raw=None):
        self.assertTrue(SCRIPT.is_file(), "The request-changes executable must exist")
        executable = self.root / "request-changes"
        shutil.copy2(SCRIPT, executable)
        content = raw if raw is not None else json.dumps(self.payload if payload is None else payload)
        target = "-" if stdin else str(self.root / "review.json")
        if not stdin:
            Path(target).write_text(content)
        return subprocess.run([str(executable), url, target], input=content if stdin else None,
                              env=self.env, capture_output=True, text=True)

    def test_submits_inline_review_with_private_token(self):
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        posted = json.loads((self.root / "posted.json").read_text())
        self.assertEqual(posted, dict(self.payload, event="REQUEST_CHANGES"))
        self.assertEqual(json.loads(result.stdout)["state"], "CHANGES_REQUESTED")
        self.assertNotIn("synthetic-review-token", result.stdout + result.stderr)

    def test_accepts_stdin_and_multiline_comments(self):
        result = self.run_script(stdin=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.root / "posted.json").read_text())["comments"], self.payload["comments"])

    def test_rejects_changed_head_closed_pr_and_self_review(self):
        for key, value in [("AUDIT_TEST_HEAD", "b" * 40), ("AUDIT_TEST_STATE", "closed"),
                           ("AUDIT_TEST_AUTHOR", "auditor")]:
            with self.subTest(key=key):
                self.env[key] = value
                result = self.run_script()
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / "posted.json").exists())
                self.env.pop(key)
                self.env["AUDIT_TEST_HEAD"] = HEAD

    def test_rejects_invalid_payloads_before_publication(self):
        bad = [dict(self.payload, commit_id=""), dict(self.payload, body=""),
               dict(self.payload, event="APPROVE"), dict(self.payload, comments="invalid"), dict(self.payload, comments=False),
               dict(self.payload, comments=[{"path": "src/x.ts", "body": "Fix it"}]),
               dict(self.payload, comments=[dict(self.payload["comments"][0], line=0)])]
        for payload in bad:
            with self.subTest(payload=payload):
                result = self.run_script(payload)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / "posted.json").exists())

    def test_rejects_malformed_or_multiple_json_documents(self):
        for content in ["{invalid", json.dumps(self.payload) + " " + json.dumps(self.payload)]:
            with self.subTest(content=content):
                result = self.run_script(raw=content)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse((self.root / "posted.json").exists())

    def test_rejects_duplicate_inline_comments(self):
        comment = self.payload["comments"][0]
        result = self.run_script(dict(self.payload, comments=[comment, dict(comment)]))
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "posted.json").exists())

    def test_keeps_distinct_findings_at_the_same_location(self):
        comment = self.payload["comments"][0]
        comments = [comment, dict(comment, body="`other-defect` Major: handle the retry race.")]
        result = self.run_script(dict(self.payload, comments=comments))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads((self.root / "posted.json").read_text())["comments"], comments)

    def test_accepts_review_without_inline_location(self):
        result = self.run_script(dict(self.payload, comments=[]))
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_rejects_invalid_pr_url(self):
        result = self.run_script(url="https://example.org/repo/pull/123")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "posted.json").exists())

    def test_rejects_missing_credentials(self):
        (self.root / ".env").unlink()
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "posted.json").exists())

    def test_propagates_publication_failure(self):
        self.env["AUDIT_TEST_FAIL_POST"] = "1"
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("API unavailable", result.stderr)


if __name__ == "__main__":
    unittest.main()
