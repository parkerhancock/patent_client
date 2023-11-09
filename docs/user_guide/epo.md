# European Patent Office

First, read the {doc}`/getting_started` page to set up EPO OPS access.

## Inpadoc

The EPO provides access to the Inpadoc database, which is roughly commensurate
with the Espacenet database. You can fetch bibliographic information quickly and easily as:

```python
>>> from patent_client import Inpadoc
>>> case = Inpadoc.objects.get("EP1000000A1")
>>> case.title
'Apparatus for manufacturing green bricks for the brick manufacturing industry'

```

Each case can also access Full Text, Images, and Inpadoc Families

```python
>>> from patent_client import Inpadoc
>>> from pprint import pprint
>>> case = Inpadoc.objects.get("EP1000000A1")
>>> pprint(list(case.family))
[FamilyMember(publication_number=EP1000000A1),
 FamilyMember(publication_number=EP1000000B1),
 FamilyMember(publication_number=ATE232441T1),
 FamilyMember(publication_number=DE69905327D1),
 FamilyMember(publication_number=NL1010536C2),
 FamilyMember(publication_number=US6093011A)]

>>> case.images.full_document.sections
[Section(name='ABSTRACT', start_page=1), Section(name='BIBLIOGRAPHY', start_page=1), Section(name='CLAIMS', start_page=3), Section(name='DESCRIPTION', start_page=2), Section(name='DRAWINGS', start_page=5), Section(name='SEARCH_REPORT', start_page=11)]
>>> case.images.full_document.download() # doctest: +SKIP
Downloads a .pdf of the document to the current directory
```

### Filter (Search)

Inpadoc records are also searchable by keyword or key phrase. Common searches are
available through the .filter interface. The filter parameters are resolved into a
CQL query, which is documented fully [here]. If you wish to pass through a
raw CQL query, just pass it as a 'cql_query' keyword argument to the filter. e.g.:

```python
>>> results = Inpadoc.objects.filter(cql_query='pa="Google LLC"')
>>> len(results) > 500
True

```

Most of the CQL filters are available through the following convenience keyword arguments:

| Keyword                       | CQL Equivalent       | Notes                                   |
| ----------------------------- | -------------------- | --------------------------------------- |
| title                         | title                |                                         |
| abstract                      | abstract             |                                         |
| title_and_abstract            | titleandabstract     |                                         |
| inventor                      | inventor             |                                         |
| applicant                     | applicant            |                                         |
| inventor_or_applicant         | inventorandapplicant |                                         |
| epodoc_publication            | spn                  |                                         |
| epodoc_application            | sap                  |                                         |
| priority                      | prioritynumber       |                                         |
| epodoc_priority               | spr                  |                                         |
| number                        | num                  | Pub, App, or Priority Number            |
| publication_date              | publicationdate      |                                         |
| citation                      | citation             |                                         |
| cited_in_examination          | ex                   |                                         |
| cited_in_opposition           | op                   |                                         |
| cited_by_applicant            | rf                   |                                         |
| other_citation                | oc                   |                                         |
| family                        | famn                 |                                         |
| cpc_class                     | cpc                  |                                         |
| ipc_class                     | ipc                  |                                         |
| ipc_core_invention_class      | ci                   |                                         |
| ipc_core_additional_class     | cn                   |                                         |
| ipc_advanced_class            | ai                   |                                         |
| ipc_advanced_additional_class | an                   |                                         |
| ipc_advanced_class            | a                    |                                         |
| ipc_core_class                | c                    |                                         |
| classification                | cl                   | IPC or CPC Class                        |
| full_text                     | txt                  | title, abstract, inventor and applicant |

The two that are missing are "publication" and "application." Those are two very common lookups that
are handled differently. When publication or application is used as a keyword argument, the value is
directly converted into the doc_db format, and the corresponding document is returned. Note that sometimes
a .get will fail with application or publication if the kind code is not used. For example, EP applications
frequently publish multiple times, so there may be an A1, A2, or A4 publication. Searches for EP100000 will
thus return EP100000A1, EP100000A2, and EP100000A4. A filter will return all of them, and a get request will
fail for mutiple records.

If you wish to use the publication or application fields on the search interface, pass them as a query to
cql_query.

## EPO Register

:::{warning}
EPO register is still a work in progress, and is currently not working in v.3.
:::

Patent Client can also retrive bibliographic and status information from the EP register.

```python
>>> from patent_client import Epo #doctest:+SKIP
>>> pub = Epo.objects.get("EP3221665A1") #doctest:+SKIP
http://ops.epo.org/3.2/rest-services/number-service/publication/original/EP3221665A1)/epodoc {}
http://ops.epo.org/3.2/rest-services/register/publication/epodoc/EP.3221665.A1/biblio {}
>>> pub.status[0] #doctest:+SKIP
{'description': 'Request for examination was made', 'code': '15', 'date': '20170825'}
>>> pub.title #doctest:+SKIP
'INERTIAL CAROUSEL POSITIONING'
>>> pub.procedural_steps[0] #doctest:+SKIP
http://ops.epo.org/3.2/rest-services/register/publication/epodoc/EP.3221665.A1/procedural-steps {}
{'phase': 'undefined', 'description': 'Renewal fee payment - 03', 'date': '20171113', 'code': 'RFEE'}
```

Searching is not available at present.

Original API URL: <http://ops.epo.org>

[here]: https://worldwide.espacenet.com/help?locale=en_EP&topic=smartsearch&method=handleHelpTopic
