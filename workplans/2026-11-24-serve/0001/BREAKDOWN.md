# Breakdown

1. ops.py: `save_document` checks the branch and the name against
   `DOCUMENT` (from 0000), refuses a task directory that does not
   exist, and writes the file.
2. ops.py: `merge` gains `message`; with it, the draft holds the
   message and the commit opens no editor; the checks before the
   commit are shared with `merge_message`.
3. tests: writes outside the four names, or on another branch, fail;
   merge with a message gives that message.
