# Breakdown

1. plans.py: `title_of(text)` and `goal_of(text)` beside `title` and
   `goal`, which call them; `branches()` maps each workplan id to its
   definition branch, local first, then origin; `read_ref(ref, path)`.
2. ops.py: `ref_status(wid, ref, master)`: tasks from the branch's
   WORKPLAN.md and task directories; states from master and the
   branch's history, the Dropped section and the files.
3. ops.py: `status` falls back to `ref_status` for an id held only on
   a branch; both carry `source` and `editable`.
4. ops.py: `workplans(master)` and `document(wid, name)`, where name is
   WORKPLAN.md or <nnnn>/TASK.md, BREAKDOWN.md or NOTES.md.
5. tests: a workplan pushed from one clone shows in another clone's
   status, read-only, without checking out its branch.
6. README.md: the `status` row names workplans on other branches.
