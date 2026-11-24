# Breakdown

1. serve.py: the handler routes GET, POST, PUT and DELETE under /api/
   through `Registry.match`, collects the values, takes the lock for
   anything but GET, and calls the command.
2. serve.py: delete `read`, `run` and `NotFound`; keep the page files,
   the checks and the JSON replies.
3. tests/test_serve.py: each test calls the new route for its step.
4. README.md, Serve: the API's routes follow the command names.
