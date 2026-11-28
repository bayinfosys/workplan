# PROTOCOL.md for SPEC.md, master as the parent branch, and wp throughout the documents

workplans/README.md links PROTOCOL.md and matches the init template;
one sentence in PROTOCOL.md and one in README.md say that master
refers to the parent branch of the workplan branch; the documents give
every command as `wp`.

Effects:

- workplans/README.md has the text of
  src/workplan/templates/project/README.md: the protocol link is
  PROTOCOL.md, and BACKLOG.md and dispatch.sh are listed
- PROTOCOL.md, under the terms table: "master", in this document and
  in the `workplan` command's help and prompts, refers to the parent
  branch of the workplan branch
- README.md, in Commands, the same sentence
- README.md, GETTING_STARTED.md and PROTOCOL.md give every command
  line, in code blocks and in prose, as `wp <command>`: README.md's
  Manual mode, Changelog, Configuration, Routing, Serve and Removing
  workplan sections among them
- README.md's Install and GETTING_STARTED.md's Install say: the
  command is `wp`; `workplan` is its full name, for use where WP-CLI's
  `wp` is installed
- README.md's Commands says every command also runs as `workplan`, in
  place of "Every command also runs as `wp`"
- the package, the repository, the program and the protocol keep the
  name workplan in prose; the help text, the prompts and the code are
  unchanged

Depends: none
Change: docs
Audience: users
