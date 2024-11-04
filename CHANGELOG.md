# Changelog
## 5.0.18 (2024-11-04)
- Update `hishel` dependency to fix issue with file downloads.

## 5.0.17 (2024-09-24)
- Update USPTO ODP to work with ODP versoion 1.0.0

## 5.0.16 (2024-07-02)
- Add `document_title` to PTAB model

## 5.0.14 (2024-05-22)
- Update underlying dependencies

## 5.0.13 (2024-05-08)
- Remove nest_asyncio call, and update Legal Codes. (#153)

## 5.0.5 (2024-05-02)
- Fix issue where ODP API returns 404 when there are no results - now returns an empty manager.
- Fix issue where older applications don't have certain fields set in ODP.

## 5.0.4 (2024-05-02)
- Fix importing of USPTO Open Data Portal models from top level patent_client object.

## 5.0.3 (2024-05-02)
- Add missing confirmation number to PEDS model (#135).
- Improve downloading of images from USPTO Public Search.

## 5.0.2 (2024-05-01)
- Fix issue where legal codes database can aggregate to an unreasonable size (#146)

## 5.0.1 (2024-05-01)
- Fix type annotations to be supported by Python 3.9 (#153, #138).
- Raises an exception in PEDS when data removed by the USPTO is attempted to be accessed.
- Fixed issue with downloading documents from EPO OPS (#151)

## 5.0.0 (2024-04-25)
- Add support for the USPTO Open Data Portal
- Restructure the API to cleanly separate async and sync models

## 4.1.2 (2023-12-04)
- Fix issue with downloads when the response does not have a `Content-Length` header
- Add more informative error messages when PEDS is down.

## 4.1.1 (2023-11-31)
- Fix issue with date filtering on PEDS endpoint

## 4.1.0 (2023-11-14)
- Add improved logic for file downloads
- Add support for USPTO BDSS

## 4.0.0 (2023-11-09)
- Rewrite all models using Pydantic models

## 3.2.11 (2023-11-09)
- Remove `requests-cache` as a dependency and remove all references thereto.

## 3.2.10 (2023-10-31)
- Attempt to fix broken docs

## 3.2.9 (2023-10-31)
- Add `download_image` to EPO OPS published model.
- Substitute `httpx` for all `requests` methods.
- Migrate cache from `requests-cache` to `hishel`
- Add async variations for all model endpoints using `hishel.AsyncCacheClient`

## 3.2.8 (2023-10-25)
- Change behavior of PTAB model downloading to match other download functions.

## 3.2.7 (2023-07-10)
- Used HTTPX for Public Patent Search and removed references in documentation suggesting it no longer works.

## 3.2.6 (2023-06-12)
- Fixed issue where Assignments would fail if a property was missing an appl_id
- Run pre-commit hooks

## 3.1.0 (2023-01-19)

- Added support for USPTO's Public Search feature and related documentation
- Continue adjusting cache configuration

## 3.0.6 (2023-01-14)

- Adjust cache configuration to prevent unexpected failures

## 3.0.5 (2022-11-17)

- Remedied issue where EPO occasionally can't find the legal code database by including a fallback code file

## 3.0.1 (2022-08-09)

- Released new major version. Will try to keep this somewhat updated!

## 2.1.3 (2020-11-12)

- Added support for USPTO's Full Text databases
- Added corresponding documentation

## 2.1.0 (2021-03-23)

- Add support for document downloads from the USPTO PEDS interface
- Fix flakey tests
- Update dependencies

## 2.0.3 (2020-10-14)

- Merge pull request ensuring that INPADOC produces consistent typing (PR #37)
- Update dev dependencies in Pipfile

## 2.0.2 (2020-04-13)

- Added foreign priority support back to PEDS API
- Revised and simplified documentation to match v.2, including using Sphinx Autodoc
- Added doctest support to documentation to confirm examples still work
- Added docstrings throughout
- Labeled some broken things as broken

## 2.0.1 (2020-03-12)

- Fixed problem where Inpadoc was indexing improperly

## 2.0.0 (2020-03-11)

- Major update with breaking API changes
- Refactored all API's to use requests_cache rather than custom caching scheme
- Uses Marshmallow for data validation, and memory-efficient dataclasses for all objects
- As part of the above, all API's now re-use the same requests.Session() object
- Deleted a ton of unnecessary code (Deleted code == debugged code)
- NOTE: Documentation not yet up-to-date. That is the next project

## 0.4.0 (2019-01-30)

- Renewed commitment to adhere to semantic versioning
- Added several new synthetic data attributes, including expiration date calculations
- General updates and improvements, including an overhaul of the base Manager and Model classes

## 0.2.3 (2018-11-02)

- Added parser for Inpadoc claims so they have an object repesentation

## 0.1.5 (2018-10-25)

- Massive refactor of OPS client

## 0.1.4 (2018-10-24)

- Support for USPTO Applications, Assignments, and PTAB documents
- Support for EPO Inpadoc and EPO Register
- Initial Installation and Getting Started Documentation

## 0.0.1 (2018-10-15)

- First release on PyPI.
- Support for EPO OPS (except Classification data)
