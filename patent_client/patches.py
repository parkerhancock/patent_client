# Necessary due to AnyIO error


def patch_response():
    from httpcore import _models

    class SafeResponse(_models.Response):
        async def safe_aclose(self: _models.Response) -> None:
            try:
                return await super().aclose()
            except RuntimeError:
                pass  # Occasionally this gets called after the event loop is closed. We don't care then.

    _models.Response = SafeResponse


def patch_ssl():
    import ssl

    class SafeSSLObject(ssl.SSLObject):
        def read(self, len=1024, buffer=None):
            try:
                return super().read(len, buffer)
            except ssl.SSLWantReadError:
                return b""

    ssl.SSLObject = SafeSSLObject
