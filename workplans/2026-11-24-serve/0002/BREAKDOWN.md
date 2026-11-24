# Breakdown

1. serve.py: a ThreadingHTTPServer bound to 127.0.0.1 holding the
   token and a lock; a handler serving index.html, app.js and app.css
   from the package's web/ directory, and the API under /api/.
2. serve.py: the API routes, each calling one operation and returning
   its data as JSON; config loaded per request.
3. cli.py: `serve` with `--port`, default 8765; prints the URL and runs
   until interrupted.
4. src/workplan/web/index.html: a page naming workplan, until 0003.
5. pyproject.toml: package-data includes web/*.
6. tests/test_serve.py: the server on port 0 in a subprocess; token
   and Host checks, reads, a document write, the patch loop, a busy
   lock, and a read-only workplan refusing writes.
7. README.md: a Serve section and the commands table row.
