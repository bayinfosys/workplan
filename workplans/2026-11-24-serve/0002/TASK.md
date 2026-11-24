# Serve the operations over HTTP on 127.0.0.1

`workplan serve [--port N]` starts a standard-library HTTP server on
127.0.0.1, prints its URL with a token, serves the page's files from
src/workplan/web/, and answers a JSON API over the operations.

Effects:

- every /api request needs the token, in an X-Workplan-Token header,
  and a Host of 127.0.0.1 or localhost on the server's port; others get
  403
- reads: workplans, status, a document, a diff, the merge message
- writes: saving a document, and running plan, define-tasks,
  produce-patch, apply, accept, reject or merge, one at a time; a
  second operation while one runs gets 409
- a failed operation answers 400 with its message
- the wheel holds src/workplan/web/
- README.md has a section on serve, and the commands table a row

Depends on 0000, 0001.
