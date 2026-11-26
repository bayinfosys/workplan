"""PROTOCOL.md gives every protocol command as git commands."""

import sys
import unittest
from pathlib import Path

from support import SRC

sys.path.insert(0, str(SRC))

from workplan.commands import registry  # noqa: E402

PROTOCOL = SRC.parent / "PROTOCOL.md"


class Protocol(unittest.TestCase):
    def test_the_protocol_commands(self):
        self.assertEqual(sorted(c.name for c in registry.commands if c.protocol), sorted([
            "init", "new", "edit", "merge", "task add", "task gen", "task edit", "task drop",
            "patch add", "patch gen", "patch apply", "patch accept", "patch reject",
            "patch drop"]))

    @unittest.skipUnless(PROTOCOL.is_file() and "\n## wp " in PROTOCOL.read_text(),
                         "PROTOCOL.md gives no commands yet")
    def test_each_has_a_section(self):
        headings = [line[3:].strip() for line in PROTOCOL.read_text().splitlines()
                    if line.startswith("## ")]
        for command in registry.commands:
            if command.protocol:
                self.assertIn(f"wp {command.name}", headings)


if __name__ == "__main__":
    unittest.main()
