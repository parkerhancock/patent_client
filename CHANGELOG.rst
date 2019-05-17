
Changelog
=========

1.1.4 (2019-05-17)
------------------
* Refactored all API's to use requests_cache rather than custom caching scheme
* As part of the above, all API's now re-use the same requests.Session() object
* USApplication.assignments are now natively provided by the PEDS api, so related Assignment objects moved to USApplication.related_assignments
* EDIS updated and now has better test coverage
* Deleted a ton of unnecessary code (Deleted code == debugged code)

0.4.0 (2019-01-30)
------------------
* Renewed commitment to adhere to semantic versioning
* Added several new synthetic data attributes, including expiration date calculations
* General updates and improvements, including an overhaul of the base Manager and Model classes

0.2.3 (2018-11-02)
------------------
* Added parser for Inpadoc claims so they have an object repesentation

0.1.5 (2018-10-25)
------------------
* Massive refactor of OPS client

0.1.4 (2018-10-24)
------------------
* Support for USPTO Applications, Assignments, and PTAB documents
* Support for EPO Inpadoc and EPO Register
* Initial Installation and Getting Started Documentation

0.0.1 (2018-10-15)
------------------

* First release on PyPI.
* Support for EPO OPS (except Classification data)
