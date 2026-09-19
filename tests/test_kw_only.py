# SPDX-License-Identifier: MIT

"""
Tests for the merging rules of class-level and field-level *kw_only*:

- A class-level *kw_only* is only the default for the class's own fields
  that don't set *kw_only* explicitly.
- An explicit field-level True or False always wins.
- A subclass's class-level *kw_only* never modifies inherited fields.
- The historic force-override behavior is only applied when the compat
  switch `attr.set_force_kw_only_override` is enabled.
"""

import inspect

import pytest

import attr
import attrs

from attr import _config


def _kinds(cls):
    """
    Map the parameters of *cls*' generated __init__ (except self) to their
    `inspect.Parameter` kinds.
    """
    params = inspect.signature(cls.__init__).parameters

    return {name: p.kind for name, p in params.items() if name != "self"}


POS = inspect.Parameter.POSITIONAL_OR_KEYWORD
KW = inspect.Parameter.KEYWORD_ONLY


@pytest.fixture(name="force_kw_only_override")
def _force_kw_only_override():
    """
    Enable the historic class-level kw_only override behavior and restore
    the default afterwards.
    """
    _config.set_force_kw_only_override(True)
    yield
    _config.set_force_kw_only_override(False)


class TestKwOnlyMerging:
    """
    Merging of class-level and field-level kw_only.
    """

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_field_false_overrides_class_true(self, decorator):
        """
        A field-level kw_only=False wins over a class-level kw_only=True,
        both in inspect.signature and in actual calls.
        """

        @decorator(kw_only=True)
        class C:
            x = attr.ib(kw_only=False)
            y = attr.ib()

        assert [a.kw_only for a in C.__attrs_attrs__] == [False, True]
        assert _kinds(C) == {"x": POS, "y": KW}

        # x can be passed positionally ...
        c = C(1, y=2)
        assert (c.x, c.y) == (1, 2)

        # ... and by keyword.
        c = C(x=1, y=2)
        assert (c.x, c.y) == (1, 2)

        # y cannot be passed positionally.
        with pytest.raises(TypeError):
            C(1, 2)

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_field_true_wins_without_class_level(self, decorator):
        """
        A field-level kw_only=True works without a class-level setting.
        """

        @decorator
        class C:
            x = attr.ib(kw_only=True)
            y = attr.ib()

        assert [a.kw_only for a in C.__attrs_attrs__] == [True, False]
        assert _kinds(C) == {"x": KW, "y": POS}

        c = C(1, x=2)
        assert (c.x, c.y) == (2, 1)

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_class_level_is_default_for_unset_fields(self, decorator):
        """
        Fields that don't set kw_only inherit the class-level setting.
        """

        @decorator(kw_only=True)
        class C:
            x = attr.ib()
            y = attr.ib(default=1)

        assert [a.kw_only for a in C.__attrs_attrs__] == [True, True]
        assert _kinds(C) == {"x": KW, "y": KW}

        with pytest.raises(TypeError):
            C(1, 2)

        c = C(x=1)
        assert (c.x, c.y) == (1, 1)

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_class_level_false_leaves_fields_positional(self, decorator):
        """
        Without a class-level setting, unset fields stay positional.
        """

        @decorator
        class C:
            x = attr.ib()
            y = attr.ib(default=1)

        assert [a.kw_only for a in C.__attrs_attrs__] == [False, False]
        assert _kinds(C) == {"x": POS, "y": POS}

        c = C(1, 2)
        assert (c.x, c.y) == (1, 2)

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_subclass_does_not_modify_base_fields(self, decorator):
        """
        A subclass's class-level kw_only doesn't change the calling
        convention of inherited fields -- over multiple inheritance levels.
        """

        @decorator
        class A:
            a = attr.ib()

        @decorator(kw_only=True)
        class B(A):
            b = attr.ib()

        @decorator
        class C(B):
            c = attr.ib()

        # The base classes' own attributes are untouched.
        assert [a.kw_only for a in A.__attrs_attrs__] == [False]
        assert [a.kw_only for a in B.__attrs_attrs__] == [False, True]

        assert [a.kw_only for a in C.__attrs_attrs__] == [False, True, False]
        assert _kinds(C) == {"a": POS, "b": KW, "c": POS}

        c = C(1, 2, b=3)
        assert (c.a, c.b, c.c) == (1, 3, 2)

        with pytest.raises(TypeError):
            C(1, 2, 3)

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_subclass_kw_only_does_not_allow_reordering_base(self, decorator):
        """
        A subclass's class-level kw_only doesn't make an inherited field
        with a default keyword-only, so a mandatory positional field can't
        follow it -- like dataclasses.
        """

        @decorator
        class Base:
            x = attr.ib(default=0)

        with pytest.raises(ValueError) as ei:

            @decorator(kw_only=True)
            class C(Base):
                y = attr.ib(kw_only=False)

        assert ei.value.args[0].startswith(
            "No mandatory attributes allowed after an attribute with a "
            "default value or factory."
        )

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_default_then_mandatory_positional_raises(self, decorator):
        """
        Within one class, a positional field with a default can't be
        followed by a mandatory positional field -- even if the class-level
        kw_only is True.
        """
        with pytest.raises(ValueError) as ei:

            @decorator(kw_only=True)
            class C:
                x = attr.ib(default=0, kw_only=False)
                y = attr.ib(kw_only=False)

        assert ei.value.args[0].startswith(
            "No mandatory attributes allowed after an attribute with a "
            "default value or factory."
        )

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_kw_only_default_allows_mandatory_after(self, decorator):
        """
        A field with a default that is keyword-only (via the class-level
        default) can be followed by a mandatory positional field.
        """

        @decorator(kw_only=True)
        class C:
            x = attr.ib(default=0)
            y = attr.ib(kw_only=False)

        assert [a.kw_only for a in C.__attrs_attrs__] == [True, False]
        assert _kinds(C) == {"x": KW, "y": POS}

        c = C(1)
        assert (c.x, c.y) == (0, 1)

        c = C(1, x=2)
        assert (c.x, c.y) == (2, 1)

    def test_make_class(self):
        """
        make_class passes kw_only through and honors explicit field-level
        settings.
        """
        C = attr.make_class(
            "C",
            {"x": attr.ib(kw_only=False), "y": attr.ib()},
            kw_only=True,
        )

        assert [a.kw_only for a in C.__attrs_attrs__] == [False, True]
        assert _kinds(C) == {"x": POS, "y": KW}

        c = C(1, y=2)
        assert (c.x, c.y) == (1, 2)

    def test_these(self):
        """
        Fields passed via these= follow the same merging rules.
        """

        @attr.s(
            kw_only=True,
            these={"x": attr.ib(kw_only=False), "y": attr.ib()},
        )
        class C:
            pass

        assert [a.kw_only for a in C.__attrs_attrs__] == [False, True]
        assert _kinds(C) == {"x": POS, "y": KW}

    @pytest.mark.parametrize("slots", [True, False])
    def test_signature_matches_calls(self, slots):
        """
        inspect.signature and actual call behavior agree for a mixed class.
        """

        @attrs.define(kw_only=True, slots=slots)
        class C:
            a: int
            b: int = attrs.field(kw_only=False)
            c: int = attrs.field(kw_only=False, default=3)
            d: int = attrs.field(default=4)

        assert _kinds(C) == {"a": KW, "b": POS, "c": POS, "d": KW}

        c = C(2, a=1)
        assert (c.a, c.b, c.c, c.d) == (1, 2, 3, 4)

        c = C(2, 5, a=1, d=6)
        assert (c.a, c.b, c.c, c.d) == (1, 2, 5, 6)

        # a and d are keyword-only.
        with pytest.raises(TypeError):
            C(1, 2, 3, 4)

        # b is mandatory.
        with pytest.raises(TypeError):
            C(a=1)

    def test_match_args(self):
        """
        __match_args__ only contains fields that can be passed positionally.
        """

        @attrs.define(kw_only=True)
        class C:
            x: int = attrs.field(kw_only=False)
            y: int = attrs.field()

        assert C.__match_args__ == ("x",)


class TestForceKwOnlyOverride:
    """
    The historic class-level kw_only override behavior is only applied when
    the compat switch is enabled.
    """

    def test_default_is_off(self):
        """
        The compat switch is off by default.
        """
        assert _config._force_kw_only_override is False
        assert attr.get_force_kw_only_override() is False

    def test_wrong_type(self):
        """
        Passing anything else than a boolean raises TypeError.
        """
        with pytest.raises(TypeError) as e:
            _config.set_force_kw_only_override("yes")

        assert "'force' must be bool." == e.value.args[0]

    def test_set_get(self):
        """
        The switch can be enabled and disabled again.
        """
        _config.set_force_kw_only_override(True)
        assert _config._force_kw_only_override is True
        assert attr.get_force_kw_only_override() is True

        _config.set_force_kw_only_override(False)
        assert _config._force_kw_only_override is False
        assert attr.get_force_kw_only_override() is False

    @pytest.mark.usefixtures("force_kw_only_override")
    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_forces_all_fields_kw_only(self, decorator):
        """
        If enabled, a class-level kw_only=True converts all fields --
        including explicit kw_only=False ones.
        """

        @decorator(kw_only=True)
        class C:
            x = attr.ib(kw_only=False)
            y = attr.ib()

        assert [a.kw_only for a in C.__attrs_attrs__] == [True, True]
        assert _kinds(C) == {"x": KW, "y": KW}

        with pytest.raises(TypeError):
            C(1, y=2)

        c = C(x=1, y=2)
        assert (c.x, c.y) == (1, 2)

    @pytest.mark.usefixtures("force_kw_only_override")
    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_forces_inherited_fields_kw_only(self, decorator):
        """
        If enabled, a class-level kw_only=True propagates to inherited
        fields (but doesn't modify the base class itself).
        """

        @decorator
        class Base:
            x = attr.ib(default=0)

        @decorator(kw_only=True)
        class C(Base):
            y = attr.ib()

        assert [a.kw_only for a in C.__attrs_attrs__] == [True, True]
        assert _kinds(C) == {"x": KW, "y": KW}

        with pytest.raises(TypeError):
            C(1, y=2)

        c = C(x=1, y=2)
        assert (c.x, c.y) == (1, 2)

        assert Base.__attrs_attrs__[0].kw_only is False

    @pytest.mark.usefixtures("force_kw_only_override")
    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_no_override_without_class_level(self, decorator):
        """
        If enabled but the class doesn't set kw_only, nothing changes.
        """

        @decorator
        class C:
            x = attr.ib()
            y = attr.ib(kw_only=True)

        assert [a.kw_only for a in C.__attrs_attrs__] == [False, True]
        assert _kinds(C) == {"x": POS, "y": KW}

        c = C(1, y=2)
        assert (c.x, c.y) == (1, 2)

    @pytest.mark.parametrize("decorator", [attr.s, attrs.define])
    def test_only_overrides_when_enabled(
        self, decorator, force_kw_only_override
    ):
        """
        The same class shape behaves differently depending on the switch:
        force-override only happens while it is enabled.
        """

        def make():
            @decorator(kw_only=True)
            class C:
                x = attr.ib(kw_only=False)
                y = attr.ib()

            return C

        # Enabled: historic force-override.
        C = make()
        assert [a.kw_only for a in C.__attrs_attrs__] == [True, True]

        # Disabled again: field-level False wins.
        _config.set_force_kw_only_override(False)
        C = make()
        assert [a.kw_only for a in C.__attrs_attrs__] == [False, True]
