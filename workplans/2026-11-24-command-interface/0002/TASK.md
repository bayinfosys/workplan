# The API from the registry

serve.py answers every /api request by matching it to a command
through the registry, in place of its own routes.

Effects:

- the routes are those of decision 6; `read`, `run`, `/api/run`,
  `/api/document`, `/api/diff`, `/api/merge-message` and
  `/api/workplans` are removed
- GET runs alongside other requests; every other method takes the
  write lock and gets 409 while another holds it
- the token and Host checks apply to every /api route, as now
- path values come from the route, query values from the query
  string, body values from the JSON body
- CLI-only commands answer 404 over HTTP
- tests/test_serve.py drives the new routes

Depends on 0001.
