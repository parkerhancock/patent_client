Patent Trial & Appeal Board
^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. note::
    Only publicly accessible documents are available. Any document that is marked confidential is not accessible.
    
Patent Client provides an interface to the PTAB Public API.

.. code-block:: python
    
    >>> from patent_client import PtabTrial
    >>> trial = PtabTrial.objects.get('IPR2012-00027')
    >>> trial
    <PtabTrial(trial_number=IPR2012-00027)>
    >>> trial.petitioner_party_name
    'Idle Free Systems, Inc.'
    >>> trial.patent_number
    '7591303'

Patent Client also provides individual documents as related objects.

.. code-block:: python

    >>> doc = trial.documents[0]
    >>> doc
    <PtabDocument(title=303' Patent File History)>
    >>> doc.title
    "303' Patent File History"
    >>> doc.download()
    # Downloads pdf entitled "303' Patent File History.pdf" to current directory

PtabTrial
============================

Supported Fields
-----------------

=========================   ===========================================       ===============     ================
Field Name                  Examples                                          Filterable          Sortable
=========================   ===========================================       ===============     ================
trial_number                IPR2012-00027; CBM2012-00001; DER2017-00001       YES                 YES
patent_number               9345123; 10123456;                                YES                 YES
application_number          11322006; 15123456                                YES                 YES
patent_owner_name           Google LLC; Bergstrom, Inc.                       YES                 YES
petitioner_party_name       (Same)                                            YES                 YES
prosecution_status          FWD Entered; Terminated-Settled; Instituted       YES                 YES
filing_date                 YYYY-mm-dd                                        YES                 YES
accorded_filing_date        YYYY-mm-dd                                        YES                 YES
institution_decision_date   YYYY-mm-dd                                        YES                 YES
last_modified_datetime      YYYY-mm-dd                                        YES                 YES
=========================   ===========================================       ===============     ================

Related Objects
----------------

=============== =================   =============   ============================
Attribute       Relationship Type   Object          Join Condition
=============== =================   =============   ============================
document        one-to-many         PtabDocument    trial_number=trial_number
us_application  one-to-one          USApplication   application_number=appl_id
=============== =================   =============   ============================

PtabDocument
===============================

Supported Fields
-----------------

=========================   ===========================================       ===============     ================
Field Name                  Examples                                          Filterable          Sortable
=========================   ===========================================       ===============     ================
title                       Petition; '303 File History                       YES                 YES
trial_number                IPR2012-00027; CBM2012-00001; DER2017-00001       YES                 YES
document_number             1001, 2024, 4001                                  YES                 YES
type                        exhibit, motion, reply, notice                    YES                 YES
filing_party                petitioner, patent_owner, board                   YES                 YES
filing_datetime             YYYY-mm-dd                                        YES                 YES
last_modified_datetime      YYYY-mm-dd                                        YES                 YES
=========================   ===========================================       ===============     ================

Related Objects
----------------

============    =================   ============    ===========================
Attribute       Relationship Type   Object          Join Condition
============    =================   ============    ===========================
trial           one-to-one          PtabTrial       trial_number=trial_number
============    =================   ============    ===========================


Original API URL: https://developer.uspto.gov/api-catalog/ptab-api


