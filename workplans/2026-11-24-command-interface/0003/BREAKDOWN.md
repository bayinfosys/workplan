# Breakdown

1. web/api.js: the token from the page's URL, one request function,
   and a function per command.
2. web/app.js: every `api(...)` call replaced by its api.js function.
3. web/index.html: load api.js before app.js. serve.py: serve
   /api.js with the other page files.
4. Check the page in a browser: board, panel, edit and save, the patch
   loop, merge.
5. web/app.js: only the latest drawing of the panel writes to it; a
   save redraws the panel twice, and both drawings added an Edit
   button (found in step 4, present since 2026-11-24-serve). The Gen
   patch and Gen tasks buttons take the commands' names.
