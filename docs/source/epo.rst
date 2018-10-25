######################
European Patent Office
######################

First, read the :doc:`Getting Started <getting_started>` page to set up EPO OPS access.

Inpadoc
=======
The EPO provides access to the Inpadoc database, which is roughly commensurate
with the Espacenet database. You can fetch bibliographic information quickly and easily as:

.. code-block:: python

    >>> from patent_client import Inpadoc
    >>> case = Inpadoc.objects.get('EP2906782A2')
    >>> case.title
    'ATTITUDE REFERENCE FOR TIEBACK/OVERLAP PROCESSING'
    >>> case.inventors
    ['VANSTEENWYK, BRETT']
    >>> case.priority_claims
    ['201261713164 P', '2013064552']

Each case can also access Full Text, Images, and Inpadoc Families

.. code-block:: python

    >>> from patent_client import Inpadoc
    >>> case = Inpadoc.objects.get('EP2906782A2')
    >>> list(case.family)
    [
        <Inpadoc(publication=EP2906782A2)>, 
        <Inpadoc(publication=EP2906782A4)>, 
        <Inpadoc(publication=CA2887530A1)>, 
        <Inpadoc(publication=CN104968889A)>, 
        <Inpadoc(publication=RU2015117646A)>, 
        <Inpadoc(publication=US2014102795A1)>, 
        <Inpadoc(publication=US9291047B2)>, 
        <Inpadoc(publication=US2016245070A1)>, 
        <Inpadoc(publication=US10047600B2)>, 
        <Inpadoc(publication=WO2014059282A2)>, 
        <Inpadoc(publication=WO2014059282A3)>
    ]
    >>> ca_equivalent = list(case.family)[3]
    >>> ca_equivalent.images.sections
    {'ABSTRACT': 1, 'BIBLIOGRAPHY': 1, 'CLAIMS': 2, 'DESCRIPTION': 6, 'DRAWINGS': 13}
    >>> ca_equivalent.images.download()
    # Downloads a .pdf of the document to the current directory

Filter (Search)
----------------

Inpadoc records are also searchable by keyword or key phrase. Common searches are 
available through the .filter interface. The filter parameters are resolved into a 
CQL query, which is documented fully `here`_. If you wish to pass through a 
raw CQL query, just pass it as a 'cql_query' keyword argument to the filter. e.g.:

.. code-block:: python

    >>> results = Inpadoc.objects.filter(cql_query='pa="Google LLC"')
    >>> len(results)
    215

Most of the CQL filters are available through the following convenience keyword arguments:

=============================== ======================= =========================================
Keyword                         CQL Equivalent          Notes
=============================== ======================= =========================================
title		                    title
abstract		                abstract
title_and_abstract              titleandabstract
inventor		                inventor
applicant		                applicant
inventor_or_applicant	        inventorandapplicant
epodoc_publication		        spn
epodoc_application  		    sap
priority		                prioritynumber
epodoc_priority		            spr
number		                    num                     Pub, App, or Priority Number
publication_date		        publicationdate         
citation		                citation
cited_in_examination    	    ex
cited_in_opposition	    	    op
cited_by_applicant		        rf
other_citation		            oc
family		                    famn
cpc_class		                cpc
ipc_class		                ipc
ipc_core_invention_class        ci
ipc_core_additional_class   	cn
ipc_advanced_class		        ai
ipc_advanced_additional_class   an
ipc_advanced_class		        a
ipc_core_class		            c
classification		            cl                      IPC or CPC Class
full_text		                txt                     title, abstract, inventor and applicant
=============================== ======================= =========================================

.. note::

    The two that are missing are "publication" and "application." Those are two very common lookups that
    are handled differently. When publication or application is used as a keyword argument, the value is
    directly converted into the doc_db format, and the corresponding document is returned. Note that sometimes
    a .get will fail with application or publication if the kind code is not used. For example, EP applications
    frequently publish multiple times, so there may be an A1, A2, or A4 publication. Searches for EP100000 will
    thus return EP100000A1, EP100000A2, and EP100000A4. A filter will return all of them, and a get request will
    fail for mutiple records.

    If you wish to use the publication or application fields on the search interface, pass them as a query to
    cql_query.

.. _here: https://worldwide.espacenet.com/help?locale=en_EP&topic=smartsearch&method=handleHelpTopic

EPO Register
=============

Patent Client can also retrive bibliographic and status information from the EP register.

.. code-block:: python

    >>> from patent_client import Epo
    >>> pub = Epo.objects.get("EP3221665A1")
    http://ops.epo.org/3.2/rest-services/number-service/publication/original/EP3221665A1)/epodoc {}
    http://ops.epo.org/3.2/rest-services/register/publication/epodoc/EP.3221665.A1/biblio {}
    >>> pub.status[0]
    {'description': 'Request for examination was made', 'code': '15', 'date': '20170825'}
    >>> pub.title
    'INERTIAL CAROUSEL POSITIONING'
    >>> pub.procedural_steps[0]
    http://ops.epo.org/3.2/rest-services/register/publication/epodoc/EP.3221665.A1/procedural-steps {}
    {'phase': 'undefined', 'description': 'Renewal fee payment - 03', 'date': '20171113', 'code': 'RFEE'}

Searching is not avaailable at present.

Original API URL: http://ops.epo.org