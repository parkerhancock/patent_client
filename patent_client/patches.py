# Necessary due to AnyIO error
from httpcore._models import Response


async def safe_aclose(self: Response) -> None:
    try:
        return await super().aclose()
    except RuntimeError:
        pass  # Occasionally this gets called after the event loop is closed. We don't care then.


setattr(Response, "aclose", safe_aclose)
