# Breakdown

1. index.html: the layout: top bar with the selector and New workplan;
   the workplan header; the board; the task panel; dialogs for plan
   and merge.
2. app.css: columns and cards, the panel, rendered Markdown and diffs,
   light and dark schemes.
3. app.js: the API client with the token from the URL; the Markdown
   and diff renderers; the board; the panel with tabs, edit and save;
   actions by state; dialogs; refresh every five seconds; a busy and
   error line.
4. README.md: the Serve section describes the board.
5. TODO.md: remove the serve item.
