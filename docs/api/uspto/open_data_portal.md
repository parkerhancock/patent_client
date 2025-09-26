# USPTO Open Data Portal

The Open Data Portal (ODP) is now the primary source for ``USApplication`` data within
``patent_client``. Configure the ``PATENT_CLIENT_ODP_API_KEY`` environment variable before
using any of the managers documented below.

## Synchronous

### Manager

```{eval-rst}
.. autoclass:: patent_client._sync.uspto.odp.manager.USApplicationManager
    :members:
    :undoc-members:

.. autoclass:: patent_client._sync.uspto.odp.manager.USApplicationBiblioManager
    :members:
    :undoc-members:

.. autoclass:: patent_client._sync.uspto.odp.manager.DocumentManager
    :members:
    :undoc-members:

.. autoclass:: patent_client._sync.uspto.odp.manager.ContinuityManager
    :members:
    :undoc-members:

```

### Models

```{eval-rst}
.. automodule:: patent_client._sync.uspto.odp.model
    :members:
    :undoc-members:
```

## Asynchronous

### Manager

```{eval-rst}
.. autoclass:: patent_client._async.uspto.odp.manager.USApplicationManager
    :members:
    :undoc-members:

.. autoclass:: patent_client._async.uspto.odp.manager.USApplicationBiblioManager
    :members:
    :undoc-members:

.. autoclass:: patent_client._async.uspto.odp.manager.DocumentManager
    :members:
    :undoc-members:

.. autoclass:: patent_client._async.uspto.odp.manager.ContinuityManager
    :members:
    :undoc-members:

```

### Models

```{eval-rst}
.. automodule:: patent_client._async.uspto.odp.model
    :members:
    :undoc-members:
```
