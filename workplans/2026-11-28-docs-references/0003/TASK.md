# Links to the site and PyPI in pyproject.toml and README.md

The package metadata points at the site, and README.md links the site
and the PyPI page, so that GitHub, PyPI and the site each link the
others.

Effects:

- pyproject.toml [project.urls]:
  - Homepage = "https://workplan.bayis.co.uk"
  - Documentation = "https://workplan.bayis.co.uk/getting-started.html"
  - Protocol = "https://workplan.bayis.co.uk/protocol.html"
  - Changelog = "https://workplan.bayis.co.uk/changelog.html"
  - Repository = "https://github.com/bayinfosys/workplan"
  - Issues = "https://github.com/bayinfosys/workplan/issues"
  - "Bay Information Systems" = "https://www.bayis.co.uk/"
- README.md, after its opening paragraph ("Plan and record development
  work in git..."): one line linking the site
  (https://workplan.bayis.co.uk), the PyPI page
  (https://pypi.org/project/workplan/) and the repository
  (https://github.com/bayinfosys/workplan)
- `python -m build` builds, and `twine check dist/*` passes

Depends: 0000
Change: chore
Audience: users
