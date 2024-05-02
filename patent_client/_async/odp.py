# A simple separate namespace for the USPTO's Open Data Portal.

from patent_client._async.uspto.odp.model import USApplication, USApplicationBiblio

__all__ = ["USApplication", "USApplicationBiblio"]
