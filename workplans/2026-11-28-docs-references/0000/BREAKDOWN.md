# Breakdown

1. Copy src/workplan/templates/project/README.md over
   workplans/README.md.
2. Add the master sentence under PROTOCOL.md's terms table, and to
   README.md's Commands after its second paragraph.
3. Replace each `workplan <command>` invocation in README.md,
   GETTING_STARTED.md and PROTOCOL.md with `wp <command>`; leave
   prose that names the package, the program or the protocol.
4. Rewrite the Install paragraphs on `wp` and `workplan`, and the
   "also runs as" sentence in Commands.
5. grep -nE '(^|[ `(])workplan (init|list|show|new|edit|merge|publish|task|patch|status|changelog|route|install|serve)\b'
   over the three documents prints nothing.
