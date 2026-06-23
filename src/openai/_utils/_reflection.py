from __future__ import annotations

import inspect
from typing import Any, Callable


def function_has_argument(func: Callable[..., Any], arg_name: str) -> bool:
    """Returns whether or not the given function has a specific parameter"""
    sig = inspect.signature(func)
    return arg_name in sig.parameters


def assert_signatures_in_sync(
    source_func: Callable[..., Any],
    check_func: Callable[..., Any],
    *,
    exclude_params: set[str] = set(),
    description: str = "",
) -> None:
    """Ensure that the signature of the second function matches the first."""

    check_sig = inspect.signature(check_func)
    source_sig = inspect.signature(source_func)

    errors: list[str] = []

    # Local imports to avoid changing module-level imports
    import typing
    from typing import get_origin, get_args
    import types
    import collections.abc as collections_abc

    def annotations_compatible(a: object, b: object) -> bool:
        # Fast path
        if a == b:
            return True

        # Respect inspect._empty as explicit absence of annotation
        if a is inspect._empty or b is inspect._empty:
            return a is b

        o_a = get_origin(a)
        o_b = get_origin(b)

        # Handle unions (including PEP 604 | unions)
        union_origins = (typing.Union, types.UnionType) if hasattr(types, "UnionType") else (typing.Union,)
        if o_a in union_origins or o_b in union_origins:
            args_a = get_args(a) if get_origin(a) else (a,)
            args_b = get_args(b) if get_origin(b) else (b,)

            # Try to match each element of args_a to one in args_b
            used = [False] * len(args_b)
            for aa in args_a:
                found = False
                for i, bb in enumerate(args_b):
                    if not used[i] and annotations_compatible(aa, bb):
                        used[i] = True
                        found = True
                        break
                if not found:
                    return False
            return True

        # Treat list and sequence origins as compatible (e.g., List[T] vs Sequence[T] or custom SequenceNotStr[T])
        def is_sequence_origin(o: object) -> bool:
            return o in (list, collections_abc.Sequence)

        if is_sequence_origin(o_a) and is_sequence_origin(o_b):
            args_a = get_args(a)
            args_b = get_args(b)
            if not args_a or not args_b:
                return True
            # Compare element type
            return annotations_compatible(args_a[0], args_b[0])

        # If both have origins, compare origins and args structurally
        if o_a or o_b:
            if o_a != o_b:
                return False
            args_a = get_args(a)
            args_b = get_args(b)
            if len(args_a) != len(args_b):
                return False
            return all(annotations_compatible(x, y) for x, y in zip(args_a, args_b))

        # Fallback: not compatible
        return False

    for name, source_param in source_sig.parameters.items():
        if name in exclude_params:
            continue

        custom_param = check_sig.parameters.get(name)
        if not custom_param:
            errors.append(f"the `{name}` param is missing")
            continue

        if not annotations_compatible(custom_param.annotation, source_param.annotation):
            errors.append(
                f"types for the `{name}` param are do not match; source={repr(source_param.annotation)} checking={repr(custom_param.annotation)}"
            )
            continue

    if errors:
        raise AssertionError(
            f"{len(errors)} errors encountered when comparing signatures{description}:\n\n" + "\n\n".join(errors)
        )
