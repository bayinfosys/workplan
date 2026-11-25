#!/bin/sh
# Run by `workplan route --dispatch` after each commit, when config.toml
# sets route.dispatch = "workplans/dispatch.sh": dispatch.sh <action> <target>...
action=$1; shift
case "$action" in
gen-task)
    workplan gen-task "$@" ;;
gen-patch)
    for task in "$@"; do workplan gen-patch "$task" & done; wait ;;
review)
    workplan status --json | python3 -c 'import json, sys
for task in json.load(sys.stdin)["tasks"]:
    if task["state"] == "stale":
        print(task["id"])' |
    while read -r task; do workplan gen-patch "$task" & done; wait ;;
esac
