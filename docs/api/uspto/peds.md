# Patent Examination Data System API

.. danger::

   The USPTO retired the Patent Examination Data System (PEDS) on March 14, 2025. The
   endpoints no longer resolve, and the implementation has been removed from
   ``patent_client``. Importing ``patent_client.uspto.peds`` now raises ``RuntimeError``.
   Use the :doc:`USPTO Open Data Portal <open_data_portal>` interfaces for all
   ``USApplication`` access.

This page is retained only to document the deprecation for existing users; there is no
runtime API surface remaining in the library.
