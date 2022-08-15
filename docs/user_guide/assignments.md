# US Assignments

Original API URL: <https://assignment-api.uspto.gov/documentation-patent>

:::{warning}
The SSL configuration on the Assignments API is broken. SSL verification has therefore been turned off
for the Assignment object. This means that the client is potentially vulnerable to man-in-the-middle
attacks. When the SSL configuration is fixed, an update will be pushed, and this warning removed
:::

:::{warning}
Some publicly available assignments are not available through this interface. Due to a PTO technical issue,
assignments of provisional applications are not made available when child applications are published through
this interface. They can only be viewed by looking up the provisional application on
[Patent Center](https://patentcenter.uspto.gov).
:::

:::{note}
The USPTO's API is quite slow, so expect some lag time the first time records are retreived. Caching speeds up subsequent requests
:::

Patent Client provides an interface to the USPTO's patent assignment database. You can use it like this:

```python
>>> from patent_client import Assignment
>>> assignments = Assignment.objects.filter(patent_number='9534285')
>>> len(assignments) >= 1
True
>>> assignments.first().id # doctest:+SKIP
'60613-72' 
>>> assignments.first().assignors[0].name # doctest:+SKIP
'ENTEGRIS, INC.'
>>> assignments.first().assignees[0].name # doctest:+SKIP
'TRUIST BANK, AS NOTES COLLATERAL AGENT' 

>>> assignments = Assignment.objects.filter(assignee='Google') # doctest:+SKIP
>>> len(assignments) > 200 # doctest:+SKIP
True
```

## Models

```{eval-rst}
.. automodule:: patent_client.uspto.assignment.model
    :members:
    :undoc-members:
    :exclude-members: Person
```
