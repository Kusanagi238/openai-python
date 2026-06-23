from typing import TYPE_CHECKING
from importlib import import_module

__all__ = [
    "ResponseTextDoneEvent",
    "ResponseTextDeltaEvent",
    "ResponseFunctionCallArgumentsDeltaEvent",
    "ResponseStream",
    "AsyncResponseStream",
    "ResponseStreamEvent",
    "ResponseStreamState",
    "ResponseStreamManager",
    "AsyncResponseStreamManager",
]

if TYPE_CHECKING:
    from ._events import (
        ResponseTextDoneEvent,
        ResponseTextDeltaEvent,
        ResponseFunctionCallArgumentsDeltaEvent,
    )
    from ._responses import (
        ResponseStream,
        AsyncResponseStream,
        ResponseStreamEvent,
        ResponseStreamState,
        ResponseStreamManager,
        AsyncResponseStreamManager,
    )


def __getattr__(name: str):
    if name in {
        "ResponseTextDoneEvent",
        "ResponseTextDeltaEvent",
        "ResponseFunctionCallArgumentsDeltaEvent",
    }:
        module = import_module("._events", package=__package__)
        return getattr(module, name)

    if name in {
        "ResponseStream",
        "AsyncResponseStream",
        "ResponseStreamEvent",
        "ResponseStreamState",
        "ResponseStreamManager",
        "AsyncResponseStreamManager",
    }:
        module = import_module("._responses", package=__package__)
        return getattr(module, name)

    raise AttributeError(f"module {__name__} has no attribute {name}")


def __dir__():
    return sorted(__all__)

