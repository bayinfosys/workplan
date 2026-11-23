# Take the version from git tags with setuptools-scm, and release from tags

The package's version comes from the latest `v*` tag through
setuptools-scm; `__version__` reads the installed version. A release
workflow builds the package on each push to master, and on a `v*` tag
publishes it to PyPI and creates the GitHub release.

Effects:

- a build from the tag v0.1.0 is version 0.1.0; a build from a later
  commit is a development version of the next one, with no local part
- `workplan --version` prints the installed version, and `0+unknown`
  when run from source without installing
- pyproject.toml follows the other Bay Information Systems projects:
  urls, classifiers and the setuptools-scm settings
- pushing the tag vX.Y.Z publishes workplan X.Y.Z to PyPI, with the
  repository secret PYPI_API_TOKEN, in the `release` environment
- README.md, Development, says how a release is made
- TODO.md no longer lists the dynamic version

Depends on 0005.
