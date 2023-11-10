"""Runner script for tools used in local development and CI.
Notes:
* 'test' and 'test-<python version>' commands: nox will create separate virtualenvs per python
  version, and use `poetry.lock` to determine dependency versions
* 'lint' command: tools and environments are managed by pre-commit
* All other commands: the current environment will be used instead of creating new ones
* Run `nox -l` to see all available commands
"""
from os import getenv
from os.path import join
from pathlib import Path
from shutil import rmtree

import nox
from nox_poetry import session

nox.options.reuse_existing_virtualenvs = True
nox.options.sessions = ["lint", "cov"]

LIVE_DOCS_PORT = 8181
LIVE_DOCS_IGNORE = ["*.pyc", "*.tmp", join("**", "modules", "*")]
LIVE_DOCS_WATCH = ["examples"]
CLEAN_DIRS = ["dist", "build", join("docs", "_build"), join("docs", "modules")]

PYTHON_VERSIONS = ["3.7", "3.8", "3.9", "3.10"]
SOURCE_FILES = [
    "patent_client",
]
INTEGRATION_TESTS = join("tests", "integration")
DEFAULT_COVERAGE_FORMATS = ["html", "term"]
# Run tests in parallel, grouped by test module
XDIST_ARGS = "--numprocesses=auto"


@session(python=PYTHON_VERSIONS)
def test(session):
    """Run tests in a separate virtualenv per python version"""
    test_paths = session.posargs or SOURCE_FILES
    cmd = f'pytest -rs {XDIST_ARGS} --doctest-glob="*.md"'
    session.run(*cmd.split(" "), *test_paths)


@session(python=False, name="test-current")
def test_current(session):
    """Run tests using the current virtualenv"""
    test(session)


@session(python=False)
def clean(session):
    """Clean up temporary build + documentation files"""
    for dir in CLEAN_DIRS:
        print(f"Removing {dir}")
        rmtree(dir, ignore_errors=True)


@session(python=False)
def clean_cassettes(session):
    """Clean up VCR cassettes"""
    for dir in Path(__file__).parent.glob("**/cassettes/*"):
        print(f"Removing {dir}")
        rmtree(dir, ignore_errors=True)


@session(python=False, name="cov")
def coverage(session):
    """Run tests and generate coverage report"""
    cmd = f"pytest ./patent_client -rs {XDIST_ARGS} --cov".split(" ")

    # Add coverage formats
    cov_formats = session.posargs or DEFAULT_COVERAGE_FORMATS
    cmd += [f"--cov-report={f}" for f in cov_formats]

    # Add verbose flag, if set by environment
    if getenv("PYTEST_VERBOSE"):
        cmd += ["--verbose"]
    session.run(*cmd)


@session(python=False)
def docs(session):
    """Build Sphinx documentation"""
    cmd = "sphinx-build docs docs/_build/html -j auto"
    session.run(*cmd.split(" "))


@session(python=False)
def livedocs(session):
    """Auto-build docs with live reload in browser.
    Add `--open` to also open the browser after starting.
    """
    args = ["-a"]
    args += [f"--watch {pattern}" for pattern in LIVE_DOCS_WATCH]
    args += [f"--ignore {pattern}" for pattern in LIVE_DOCS_IGNORE]
    args += [f"--port {LIVE_DOCS_PORT}", "-j auto"]
    if session.posargs == ["open"]:
        args.append("--open-browser")

    clean(session)
    cmd = "sphinx-autobuild docs docs/_build/html " + " ".join(args)
    session.run(*cmd.split(" "))


@session(python=False)
def lint(session):
    """Run linters and code formatters via pre-commit"""
    cmd = "pre-commit run --all-files"
    session.run(*cmd.split(" "))
