import warnings

warnings.warn(
    "The patent_client.uspto.peds module has been removed because the USPTO retired PEDS in March 2025. "
    "Please migrate to patent_client.uspto.odp for Open Data Portal access.",
    DeprecationWarning,
    stacklevel=2,
)

raise RuntimeError("USPTO PEDS has been retired by the USPTO. Use patent_client.uspto.odp instead.")
