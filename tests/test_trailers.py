"""A task's trailer block, read with git."""

import sys
import unittest

from support import SRC

sys.path.insert(0, str(SRC))

from workplan import plans  # noqa: E402

TASK = """# A task

The change.

Effects:

- something holds

"""


class Trailers(unittest.TestCase):
    def test_a_block_of_several_keys(self):
        text = TASK + "Depends: 0000, 0002\nChange: feat\nAudience: users\nBreaking: X is now Y\n"
        self.assertEqual(plans.trailers(text), [
            ("Depends", "0000, 0002"), ("Change", "feat"), ("Audience", "users"),
            ("Breaking", "X is now Y")])
        self.assertEqual(plans.trailer(text, "change"), "feat")
        self.assertIsNone(plans.trailer(text, "Refs"))

    def test_no_block(self):
        self.assertEqual(plans.trailers(TASK), [])
        self.assertEqual(plans.trailers(TASK + "Depends on 0001.\n"), [])

    def test_depends_from_the_trailer(self):
        self.assertEqual(plans.depends_of(TASK + "Depends: 0000, 0002\nChange: fix\n", "w"),
                         ["w/0000", "w/0002"])
        self.assertEqual(plans.depends_of(TASK + "Depends: none\nChange: fix\n", "w"), [])

    def test_depends_from_the_sentence(self):
        self.assertEqual(plans.depends_of(TASK + "Depends on 0001, 0003.\n", "w"),
                         ["w/0001", "w/0003"])
        self.assertEqual(plans.depends_of(TASK + "Depends on none.\n", "w"), [])


if __name__ == "__main__":
    unittest.main()
