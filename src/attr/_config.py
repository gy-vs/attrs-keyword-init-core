# SPDX-License-Identifier: MIT

__all__ = [
    "get_force_kw_only_override",
    "get_run_validators",
    "set_force_kw_only_override",
    "set_run_validators",
]

_run_validators = True

# Historic behavior switch: if True, a class-level ``kw_only=True`` forcibly
# converts *all* attributes -- including inherited ones and attributes that
# explicitly set ``kw_only=False`` -- to keyword-only.  If False (the
# default), the class-level setting is only a default for the class's own
# attributes that don't set ``kw_only`` explicitly.
_force_kw_only_override = False


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


def set_force_kw_only_override(force):
    """
    Set whether a class-level ``kw_only=True`` forcibly converts *all*
    attributes -- including inherited ones and those that explicitly set
    ``kw_only=False`` -- to keyword-only (the historic behavior).

    If False (the default), the class-level ``kw_only`` is only used as the
    default for the class's own attributes that don't set ``kw_only``
    explicitly, and inherited attributes are left alone.

    .. versionadded:: 26.1.0
    """
    if not isinstance(force, bool):
        msg = "'force' must be bool."
        raise TypeError(msg)
    global _force_kw_only_override
    _force_kw_only_override = force


def get_force_kw_only_override():
    """
    Return whether the historic class-level ``kw_only`` override behavior is
    enabled.

    .. versionadded:: 26.1.0
    """
    return _force_kw_only_override
