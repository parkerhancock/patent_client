Design Notes
^^^^^^^^^^^^

EPO Open Patent Services
========================

The EPO OPS system has four general APIs:

* Classifications
* Inpadoc - Keyword Search, Bibliographic Data, Fulltext Services, and Images
* EPO Register - Bib data and status information from the EPO Register
* Number Services - Conversion from original number to DocDB and EpoDoc

Inpadoc
-------
The Inpadoc service is by far the most useful API. It generally uses a "DocDB" format to
represent a "primary key" for each document, comprising:
    - Country
    - Document Number
    - Kind Code
    - Date

Documents can be located in one of two ways:
    - Keyword Search
    - Document Number Lookup (Convert from Original Number to DocDB Format)

Users will want to access Inpadoc documents primarily through the search interface,
but will also want single-document lookup. 