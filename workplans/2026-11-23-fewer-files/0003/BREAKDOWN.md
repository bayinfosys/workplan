# Breakdown

1. cli.py: delete `USAGE` and the `epilog` and `formatter_class`
   arguments of the parser.
2. cli.py: order the subparsers as the flow runs: init, plan,
   define-tasks, produce-patch, apply, diff, accept, reject, merge,
   status, route, install.
