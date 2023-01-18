# Contributing

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

## Bug reports

When [reporting a bug](https://github.com/parkerhancock/patent_client/issues) please include:

> - Your operating system name and version.
> - Any details about your local setup that might be helpful in troubleshooting.
> - Detailed steps to reproduce the bug.

## Documentation improvements

ip could always use more documentation, whether as part of the
official ip docs, in docstrings, or even on the web in blog posts,
articles, and such.

## Feature requests and feedback

The best way to send feedback is to file an issue at <https://github.com/parkerhancock/patent_client/issues>.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that code contributions are welcome :)

## Development

To set up `patent_client` for local development:

1. Fork [patent_client](https://github.com/parkerhancock/patent_client)
   (look for the "Fork" button).

2. Clone your fork locally:

   ```
   git clone git@github.com:your_name_here/patent_client.git
   ```

3. Install [Poetry](https://python-poetry.org/docs/#installation) if you don't have it already, and
   then create a virtual environment / install dependencies by running:

   ```
   poetry install
   ```

   If you want to develop the docs, add the optional documentation dependencies:

   ```
   poetry install -E docs
   ```

4. Install [pre-commit](https://pre-commit.com/) if you don't have it already, and install the
   pre-commit hooks with:

   ```
   pre-commit install
   ```

5. Run the test suite to confirm everything is working with:

   ```
   poetry run pytest
   ```

6. Create a branch for local development:

   ```
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

7. Commit your changes and push your branch to GitHub:

   ```
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

8. Submit a pull request through the GitHub website.

### Pull Request Guidelines

If you need some code review or feedback while you're developing the code just make the pull request.

For merging, you should:

1. Update documentation when there's new API, functionality etc.
2. Add a note to `CHANGELOG.rst` about the changes.
3. Add yourself to `AUTHORS.rst`.

### Tips

To avoid having to prefix commands with `poetry run`, create a shell inside the virtualenv with:

```
poetry shell
```

To run a subset of tests, either call pytest with the test file, or use a keyword:

```
poetry run pytest /path/to/test/file.py
```

OR

```
poetry run pytest -k "class or function name"
```
