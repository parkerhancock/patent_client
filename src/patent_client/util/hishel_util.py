from contextlib import contextmanager


@contextmanager
def cache_disabled(session):
    if hasattr(session._transport, "_transport"):
        cached_transport = session._transport._transport
        session._transport = session._transport._transport
        yield
        session._transport = cached_transport
    else:
        yield
