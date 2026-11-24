# The page through api.js

src/workplan/web/api.js holds one function per command the page uses,
each calling its route; app.js uses those functions and builds no URL
of its own.

Effects:

- api.js covers list-workplan, show-workplan, add-workplan,
  edit-workplan, merge-workplan, show-task, edit-task, gen-task,
  show-patch, gen-patch, apply-patch, accept-patch and reject-patch
- the page reads documents through show-workplan and show-task, the
  patch through show-patch, and the merge message through
  merge-workplan with show
- the page behaves as before

Depends on 0002.
