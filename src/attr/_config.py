# SPDX-License-Identifier: MIT

__all__ = [
    "get_kw_only_override",
    "get_run_validators",
    "set_kw_only_override",
    "set_run_validators",
]

_run_validators = True
_kw_only_override = False


def set_run_validators(run):
    """
    Set whether or not validators are run.  By default, they are run.

    .. deprecated:: 21.3.0 It will not be removed, but it also will not be
        moved to new ``attrs`` namespace. Use `attrs.validators.set_disabled()`
        instead.
    """
    if not isinstance(run, bool):
        msg = "'run' must be bool."
        raise TypeError(msg)
    global _run_validators
    _run_validators = run


def get_run_validators():
    """
    Return whether or not validators are run.

    .. deprecated:: 21.3.0 It will not be removed, but it also will not be
        moved to new ``attrs`` namespace. Use `attrs.validators.get_disabled()`
        instead.
    """
    return _run_validators


def set_kw_only_override(override):
    """
    Set whether or not a class-level ``kw_only=True`` forcibly converts *all*
    fields to keyword-only -- including fields that explicitly set
    ``kw_only=False`` and fields inherited from base classes.

    This is the historic behavior of *attrs*.  By default, it is disabled and
    a class-level ``kw_only`` is only a default for the class's own fields
    that don't set ``kw_only`` explicitly (mirroring `dataclasses`).

    Only enable this if you rely on the old force-override behavior; it only
    has an effect while it is enabled.

    .. versionadded:: 25.4.0
    """
    if not isinstance(override, bool):
        msg = "'override' must be bool."
        raise TypeError(msg)
    global _kw_only_override
    _kw_only_override = override


def get_kw_only_override():
    """
    Return whether or not a class-level ``kw_only=True`` forcibly overrides
    field-level ``kw_only`` settings and propagates to inherited attributes.

    .. versionadded:: 25.4.0
    """
    return _kw_only_override
