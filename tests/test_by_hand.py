"""Each command against its "By hand" block in SPEC.md.

Two repositories are built the same way, with fixed commit dates. One
runs the command and the other runs the block; their commits, trees
and files must match.
"""

import json
import tempfile
import unittest
from pathlib import Path
from string import Template

from support import SRC, Repo, agent_env, planned, scripted_agent

TEMPLATES = SRC / "workplan" / "templates"
GOAL = "app.txt says goodbye. Nothing else changes."


class ByHand(unittest.TestCase):
    def setUp(self):
        self.tool, self.hand = Repo(), Repo()
        self.tmp = tempfile.TemporaryDirectory()
        self.agent = scripted_agent(Path(self.tmp.name))
        self.env = agent_env(self.agent)

    def tearDown(self):
        self.tool.cleanup()
        self.hand.cleanup()
        self.tmp.cleanup()

    def head(self, repo: Repo) -> str:
        return repo.git("rev-parse", "HEAD")

    def both_planned(self) -> str:
        wid = planned(self.tool, agent=self.agent)
        planned(self.hand, agent=self.agent)
        return wid

    def test_init(self):
        for repo in (self.tool, self.hand):
            repo.write("app.txt", "hello\n")
            repo.commit_all("app")
        self.tool.wp("init")
        self.hand.sh(
            "mkdir -p workplans\n"
            f"cp {TEMPLATES}/project/README.md {TEMPLATES}/project/PRINCIPLES.md "
            f"{TEMPLATES}/project/BACKLOG.md {TEMPLATES}/project/config.toml "
            f"{TEMPLATES}/project/dispatch.sh workplans/\n"
            "printf '%s\\n' 'workplans/*/*/output.patch' 'workplans/*/*/COMMIT_MSG' >> .gitignore\n"
            "git add workplans .gitignore\n"
            "git commit -q -m 'workplan init'")
        self.assertEqual(self.head(self.tool), self.head(self.hand))

    def test_plan_and_gen_task(self):
        wid = planned(self.tool, agent=self.agent)

        self.hand.write("app.txt", "hello\n")
        self.hand.commit_all("app")
        self.hand.wp("init")
        plan = Template((TEMPLATES / "documents/WORKPLAN.md").read_text()).substitute(
            id=wid, title="greeting", goal=GOAL)
        plan = plan.replace("## Tasks\n\n", "## Tasks\n\n0000  Task number 0\n\n")
        task = self.tool.read(f"workplans/{wid}/0000/TASK.md")
        breakdown = self.tool.read(f"workplans/{wid}/0000/BREAKDOWN.md")
        self.hand.sh(f"git switch -q -c workplan/{wid}/definition master")
        self.hand.write(f"workplans/{wid}/WORKPLAN.md", plan)
        self.hand.write(f"workplans/{wid}/0000/TASK.md", task)
        self.hand.write(f"workplans/{wid}/0000/BREAKDOWN.md", breakdown)
        self.hand.sh(f"git add workplans/{wid}\ngit commit -q -m '{wid} define tasks'")

        self.assertEqual(self.head(self.tool), self.head(self.hand))

    def test_accept(self):
        wid = self.both_planned()
        for repo in (self.tool, self.hand):
            repo.wp("gen-patch", "0000", env=self.env)
            repo.write(f"workplans/{wid}/0000/NOTES.md", "# Notes\n")
        self.tool.wp("accept-patch", "0000")
        self.hand.sh(f"w={wid}; t=workplans/$w/0000\n"
                     "git apply --index $t/output.patch\n"
                     "git add $t workplans/$w/WORKPLAN.md\n"
                     "git commit -q -F $t/COMMIT_MSG")
        self.assertEqual(self.head(self.tool), self.head(self.hand))

    def test_reject(self):
        wid = self.both_planned()
        for repo in (self.tool, self.hand):
            repo.wp("gen-patch", "0000", env=self.env)
            repo.wp("apply-patch", "0000")
        self.tool.wp("reject-patch", "0000")
        self.hand.sh(f"git apply --index -R workplans/{wid}/0000/output.patch")
        self.assertEqual(self.tool.git("status", "--porcelain"),
                         self.hand.git("status", "--porcelain"))

    def test_gen_patch(self):
        wid = self.both_planned()
        self.tool.wp("gen-patch", "0000", env=self.env)
        wt = Path(self.tmp.name) / "wt"
        self.hand.sh(
            f"w={wid}; t=$w/0000\n"
            f"git worktree add -q --detach {wt} workplan/$w/definition\n"
            f"cp -r workplans {wt}/\n"
            f"git -C {wt} add -A && base=$(git -C {wt} write-tree)\n"
            f"( cd {wt} && WORKPLAN_ACTION=gen-patch WORKPLAN_TARGET=$t "
            f"WORKPLAN_COMMIT_MSG=workplans/$t/COMMIT_MSG {self.agent} < /dev/null > /dev/null )\n"
            "x=':(exclude)workplans/*/*/output.patch'; y=':(exclude)workplans/*/*/COMMIT_MSG'\n"
            f"git -C {wt} add -A -- . \"$x\" \"$y\"\n"
            f"git -C {wt} diff --cached --binary $base -- . \"$x\" \"$y\" "
            f"> workplans/$t/output.patch\n"
            f"cp {wt}/workplans/$t/COMMIT_MSG workplans/$t/\n"
            f"git worktree remove --force {wt}")
        for name in ("output.patch", "COMMIT_MSG"):
            path = f"workplans/{wid}/0000/{name}"
            self.assertEqual(self.tool.read(path), self.hand.read(path))

    def test_status(self):
        wid = planned(self.tool, tasks=2, agent=scripted_agent(Path(self.tmp.name), tasks=2))
        self.tool.wp("gen-patch", "0000", env=self.env)
        self.tool.wp("accept-patch", "0000")
        data = json.loads(self.tool.wp("status", "--json").stdout)
        states = {t["id"]: (t["state"], t["detail"]) for t in data["tasks"]}

        t = f"{wid}/0000"
        complete = self.tool.sh(f"git log HEAD -E --grep='^{t} ' --format='%h %s' -n 1").strip()
        merged = self.tool.sh(f"git log master -E --grep='^{t} ' --format='%h %s' -n 1").strip()
        self.assertEqual(merged, "")
        self.assertEqual(states[t], ("complete", complete))
        self.assertEqual(states[f"{wid}/0001"][0], "refinement")

    def test_merge(self):
        wid = self.both_planned()
        for repo in (self.tool, self.hand):
            repo.wp("gen-patch", "0000", env=self.env)
            repo.wp("accept-patch", "0000")

        self.tool.wp("merge-workplan")
        msg = Path(self.tmp.name) / "msg"
        self.hand.sh(
            f"w={wid}; b=workplan/$w/definition\n"
            "git merge-base --is-ancestor master $b\n"
            f"{{ echo \"$w greeting\"; echo; echo \"{GOAL}\"; echo\n"
            "  git log --reverse --format=%s master..$b | grep \"^$w/[0-9]\\{4\\} \"; echo\n"
            f"  echo \"Workplan: workplans/$w/WORKPLAN.md\"; }} > {msg}\n"
            "git switch -q master\n"
            "git merge -q --squash $b\n"
            f"git commit -q -e -F {msg}\n"
            "git branch -q -D $b")
        self.assertEqual(self.head(self.tool), self.head(self.hand))
        for repo in (self.tool, self.hand):
            self.assertEqual(repo.git("branch", "--list", f"workplan/{wid}/*"), "")


if __name__ == "__main__":
    unittest.main()
