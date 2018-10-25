US Assignments
^^^^^^^^^^^^^^^^^
.. warning::
    The SSL configuration on the Assignments API is broken. SSL verification has therefore been turned off
    for the Assignment object. This means that the client is potentially vulnerable to man-in-the-middle 
    attacks. When the SSL configuration is fixed, an update will be pushed, and this warning removed

.. warning::
    Some publicly available assignments are not available through this interface. Due to a PTO technical issue,
    assignments of provisional applications are not made available when child applications are published through
    this interface. They can only be viewed by looking up the provisional application on
    `PAIR <https://portal.uspto.gov/pair/PublicPair>`_.

.. note::
    The USPTO's API is quite slow, so expect some lag time the first time records are retreived. Caching speeds up
    subsequent requests

Patent Client provides an interface to the USPTO's patent assignment database. You can use it like this:

.. code-block:: python

    >>> from patent_client import Assignment
    >>> assignments = Assignment.objects.filter(patent='9534285')
    >>> len(assignments)
    1
    >>> assignments.first()
    <Assignment(id=34894-25)>
    >>> assignments.first().pat_assignor_name
    'ADVANCED TECHNOLOGY MATERIALS, INC.'
    >>> assignments.first().pat_assignee_name
    'ENTEGRIS, INC.'

    >>> assignments = Assignment.objects.filter(assignee='Google')
    >>> len(assignments)
    23932

USPTO Assignments
=================

Supported Fields
----------------

=========================   ===========================================       ===============     ================
Field Name                  Examples                                          Filterable          Sortable
=========================   ===========================================       ===============     ================
patent                      9534285                                           YES                 YES
application                 15710770                                          YES                 YES 
publication                 20180191929                                       YES                 YES
assignee                    GOOGLE LLC                                        YES                 YES
assignor                    MULLINS, SCOTT                                    YES                 YES
pct_application             PCT/US2005/012345                                 YES                 YES
correspondent               MORGAN, LEWIS & BOCKIUS                           YES                 YES
reel_frame                  047086-0788                                       YES                 YES
=========================   ===========================================       ===============     ================

Relationships
-------------

=============== =================   ==============  =================
Attribute       Relationship Type   Object          Join Condition
=============== =================   ==============  =================
us_applications one-to-many         USApplication   app_num=appl_id
=============== =================   ==============  =================

Original API URL: https://assignment-api.uspto.gov/documentation-patent/
