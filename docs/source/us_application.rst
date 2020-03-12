US Applications
^^^^^^^^^^^^^^^
.. warning::
    The PEDS interface is under active development by the USPTO. Occasionally documented filtering
    and ordering criteria will fail. Failed filters return no results. Failed ordering critera just
    have no effect.

Patent Client provides an interface to the USPTO Patent Examination Data System (PEDS).

PEDS is a REST-ful API that contains some - but not all - of the application data available
through PAIR. Notably, it is missing file history documents.

Nevertheless, it provides a wealth of bibliographic information on pending and issued US 
Patent applications. Use it like this:

.. code-block:: python

    >>> from patent_client import USApplication
    >>> app = USApplication.objects.get('14591909')
    >>> app.patent_title
    'Integrated Docking System for Intelligent Devices'
    >>> app.app_filing_date
    datetime.date(2015, 1, 7)
    >>> app.app_status
    'Docketed New Case - Ready for Examination'

There are also lots of filtering options, which make this interface great for patent
portfolio analysis. For example:

.. code-block:: python

    >>> apps = USApplication.objects.filter(first_named_applicant='Caterpillar')
    >>> len(apps)
    4817
    >>> apps[:5].to_list()
    [
        USApplication(appl_id='15985170', patent_title='FUEL INJECTOR AND FUEL SYSTEM WITH VALVE TRAIN NOISE SUPPRESSOR', app_status='Response to Non-Final Office Action Entered and Forwarded to Examiner'), 
        USApplication(appl_id='15837079', patent_title='SYSTEM AND METHOD FOR REDUCING CLUTCH FILL TIME', app_status='Patented Case'), 
        USApplication(appl_id='15850772', patent_title='System And Method Of Determining Remaining Useful Life Of An Air Filter', app_status='Patented Case'), 
        USApplication(appl_id='15953752', patent_title='FUEL INJECTOR ASSEMBLY HAVING A CASE DESIGNED FOR SOLENOID COOLING', app_status='Patented Case'), 
        USApplication(appl_id='15840316', patent_title='AIR INTAKE SYSTEM FOR ENGINES', app_status='Patented Case')]
    ]

US Application
==============

Supported Fields
----------------

=========================   ===========================================       ===============     ================
Field Name                  Examples                                          Filterable          Sortable
=========================   ===========================================       ===============     ================
app_attr_dock_number        GOOG292CON5, 123145.123123                        Yes                 Yes
app_cls_sub_cls             700/090000                                        Yes                 Yes
app_confr_number            2109                                              Yes                 Yes
app_control_number          <Unknown>                                         Unknown             Unknown
app_cust_number             37268                                             Yes                 Yes
app_early_pub_date          YYYY-mm-dd                                        Yes                 Yes
app_early_pub_number        US20160195856A1                                   Yes                 Yes
app_entity_status           UNDISCOUNTED; SMALL; MICRO                        Yes                 Yes
app_exam_name               CONNOLLY, MARK A                                  Yes                 Yes
app_filing_date             YYYY-mm-dd                                        Yes                 Yes
app_grp_art_number          2117                                              Yes                 Yes
app_intl_pub_date           YYYY-mm-dd                                        Yes                 Yes
app_intl_pub_number         <Unknown>                                         Unknown             Unknown
app_pct_number              <Unknown>                                         Unknown             Unknown
app_status                  Patented Case; Docketed New Case                  Yes                 Yes
app_status_date             YYYY-mm-dd                                        Yes                 Yes
app_type                    Utility, Design                                   Yes                 Yes
appl_id                     14591909                                          Yes                 Yes
first_inventor_file         Yes; No                                           Yes                 Yes
first_named_applicant       Google LLC                                        Yes                 Yes
intl_filing_date            YYYY-mm-dd                                        Yes                 Yes
patent_issue_date           YYYY-mm-dd                                        Yes                 Yes
patent_number               9151234, 10053949                                 Yes                 Yes
patent_title                "Integrated Docking System . . ."                 Yes                 Yes
primary_inventor            Yechezkal Evan Spero                              Yes                 Yes
wipo_early_pub_date         YYYY-mm-dd                                        Yes                 Yes
wipo_early_pub_number       WO20121231234                                     Yes                 Yes
=========================   ===========================================       ===============     ================

Compound Data Objects
---------------------

===================  ========================================================================================================================================
Field Name           Description
===================  ========================================================================================================================================
transactions         list of transactions (filings, USPTO actions, etc.) involving the application
child_continuity     list of child application Relationship objects
parent_continuity    list of parent application Relationship objects
foreign_priority     list of foreign applications from which the application claims priority
pta_pte_history      Patent Term Adjustment / Extension Event History
pta_pte_summary      Patent Term Adjustment / Extension Results, including total term extension
correspondent        Contact information for the prosecuting law firm
attorneys            List of attorneys authorized to take action in the case
expiration           Patent Expiration Data (earliest non-provisional US parent + 20 years + extension and a flag for the presence of a Terminal Disclaimer)
===================  ========================================================================================================================================

Relationships
-------------

============        =================   ============    ===========================================
Attribute           Relationship Type   Object          Join Condition
============        =================   ============    ===========================================
trials              one-to-many         PtabTrial       patent_number=patent_number
assignments         one-to-many         Assignment      appl_id=application
inpadoc_pub         one-to-one          Inpadoc         app_early_pub_number=publication_number        
inpadoc_pat         one-to-one          Inpadoc         patent_number=publication_number
============        =================   ============    ===========================================

Original API URL: https://ped.uspto.gov/peds/