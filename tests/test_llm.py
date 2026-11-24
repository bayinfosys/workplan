"""The none agent and the route classifier against a fake endpoint."""

import unittest

from support import FakeEndpoint, Repo, planned

DIFF = """\
--- a/app.txt
+++ b/app.txt
@@ -1 +1,2 @@
 hello
+goodbye
"""

BAD_DIFF = """\
--- a/app.txt
+++ b/app.txt
@@ -1 +1,2 @@
 not the content
+goodbye
"""


class Endpoint(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.endpoints = []

    def tearDown(self):
        self.repo.cleanup()
        for endpoint in self.endpoints:
            endpoint.close()

    def endpoint(self, replies: list[str]) -> FakeEndpoint:
        endpoint = FakeEndpoint(replies)
        self.endpoints.append(endpoint)
        return endpoint

    def none_env(self, endpoint: FakeEndpoint) -> dict:
        return {"WORKPLAN_AGENT": "none", "WORKPLAN_AGENT_MODEL": "test-model",
                "WORKPLAN_API_BASE": endpoint.base, "WORKPLAN_API_KEY": "secret"}

    def test_none_agent_defines_tasks(self):
        wid = planned(self.repo, tasks=0)
        endpoint = self.endpoint([
            "Here are the tasks.\n\n"
            f"===== workplans/{wid}/0000/TASK.md =====\n"
            "# Say goodbye\n\nAppend goodbye.\n\nDepends on none.\n"
            f"===== workplans/{wid}/0000/BREAKDOWN.md =====\n"
            "```markdown\n# Breakdown\n\n1. Append goodbye.\n```\n"
            f"===== workplans/{wid}/WORKPLAN.md =====\nignored\n"
            "===== app.txt =====\nignored\n"
        ])
        self.repo.wp("gen-task", env=self.none_env(endpoint))
        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/BREAKDOWN.md"),
                         "# Breakdown\n\n1. Append goodbye.\n")
        self.assertIn("0000  Say goodbye", self.repo.read(f"workplans/{wid}/WORKPLAN.md"))
        self.assertEqual(self.repo.read("app.txt"), "hello\n")
        prompt = endpoint.requests[0]["body"]["messages"][0]["content"]
        self.assertIn(f"===== workplans/{wid}/WORKPLAN.md =====", prompt)
        self.assertIn("Depends on $depends.", prompt)

    def test_none_agent(self):
        wid = planned(self.repo)
        endpoint = self.endpoint([f"{wid}/0000 Say goodbye\n\n```diff\n{DIFF}```\n"])
        self.repo.wp("gen-patch", "0000", env=self.none_env(endpoint))

        self.assertEqual(self.repo.read(f"workplans/{wid}/0000/COMMIT_MSG"),
                         f"{wid}/0000 Say goodbye\n")
        self.assertIn("+goodbye", self.repo.read(f"workplans/{wid}/0000/output.patch"))
        request = endpoint.requests[0]
        self.assertEqual(request["path"], "/v1/chat/completions")
        self.assertEqual(request["auth"], "Bearer secret")
        prompt = request["body"]["messages"][0]["content"]
        self.assertIn("===== app.txt =====", prompt)
        self.assertIn(f"===== workplans/{wid}/0000/TASK.md =====", prompt)

    def test_none_agent_retries_with_the_error(self):
        wid = planned(self.repo)
        endpoint = self.endpoint([
            f"{wid}/0000 Say goodbye\n\n```diff\n{BAD_DIFF}```\n",
            f"{wid}/0000 Say goodbye\n\n```diff\n{DIFF}```\n",
        ])
        self.repo.wp("gen-patch", "0000", env=self.none_env(endpoint))
        self.assertEqual(len(endpoint.requests), 2)
        retry = endpoint.requests[1]["body"]["messages"]
        self.assertEqual(len(retry), 3)
        self.assertIn("did not apply", retry[2]["content"])

    def test_none_agent_gives_up(self):
        planned(self.repo)
        endpoint = self.endpoint(["no diff here"] * 3)
        result = self.repo.wp("gen-patch", "0000", env=self.none_env(endpoint), ok=False)
        self.assertIn("3 attempts", result.stderr)

    def classify(self, answer: str) -> str:
        endpoint = self.endpoint([answer])
        env = {"WORKPLAN_ROUTE_CLASSIFIER": "llm", "WORKPLAN_ROUTE_MODEL": "small",
               "WORKPLAN_API_BASE": endpoint.base}
        result = self.repo.wp("route", env=env)
        return result.stdout.strip() + " | " + result.stderr.strip()

    def test_classifier_chooses(self):
        wid = planned(self.repo)
        out = self.classify("none")
        self.assertTrue(out.startswith("none | route: llm chose none; the rules chose gen-patch"),
                        out)

    def test_classifier_falls_back_without_targets(self):
        wid = planned(self.repo)
        out = self.classify("review")
        self.assertTrue(out.startswith(f"gen-patch {wid}/0000 | "), out)
        self.assertIn("rules chose gen-patch", out)

    def test_classifier_falls_back_on_nonsense(self):
        wid = planned(self.repo)
        out = self.classify("I am not sure")
        self.assertTrue(out.startswith(f"gen-patch {wid}/0000 | "), out)

    def test_classifier_picks_another_action_with_targets(self):
        wid = planned(self.repo)
        out = self.classify("gen-task")
        self.assertTrue(out.startswith(f"gen-task {wid} | route: llm chose gen-task"), out)


if __name__ == "__main__":
    unittest.main()
