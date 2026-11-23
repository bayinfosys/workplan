# Breakdown

1. pyproject.toml: build-system requires `setuptools>=77` (for the
   SPDX licence field) and `setuptools_scm>=8`; `version` stays in
   `dynamic`; `[tool.setuptools_scm]` with
   `local_scheme = "no-local-version"`; delete
   `[tool.setuptools.dynamic]`.
2. pyproject.toml: classifiers name Python 3.11, 3.12 and 3.13; urls
   are Homepage, Repository, Specification, Issues and Bay Information
   Systems.
3. src/workplan/__init__.py: `__version__` from
   `importlib.metadata.version("workplan")`, `0+unknown` when the
   package is not installed.
4. .github/workflows/release.yaml: on pushes to master and `v*` tags,
   check out with full history, build with `python -m build`, check
   with `twine check`; on a tag, upload with twine and run
   `gh release create --generate-notes`.
5. README.md, Development: a release is a `vX.Y.Z` tag on master,
   pushed; the workflow needs the `release` environment and the
   PYPI_API_TOKEN secret.
6. TODO.md: remove "dynamic version using `scm_tools`".
