# SPDX-License-Identifier: MIT

"""
Tests for `attr._config`.
"""

import pytest

from attr import _config


class TestConfig:
    def test_default(self):
        """
        Run validators by default.
        """
        assert True is _config._run_validators

    def test_set_run_validators(self):
        """
        Sets `_run_validators`.
        """
        _config.set_run_validators(False)
        assert False is _config._run_validators
        _config.set_run_validators(True)
        assert True is _config._run_validators

    def test_get_run_validators(self):
        """
        Returns `_run_validators`.
        """
        _config._run_validators = False
        assert _config._run_validators is _config.get_run_validators()
        _config._run_validators = True
        assert _config._run_validators is _config.get_run_validators()

    def test_wrong_type(self):
        """
        Passing anything else than a boolean raises TypeError.
        """
        with pytest.raises(TypeError) as e:
            _config.set_run_validators("False")
        assert "'run' must be bool." == e.value.args[0]


class TestKwOnlyOverride:
    @pytest.fixture(autouse=True)
    def _reset(self):
        """
        Ensure the override is disabled again after each test.
        """
        try:
            yield
        finally:
            _config.set_kw_only_override(False)

    def test_default(self):
        """
        The force-override is disabled by default.
        """
        assert False is _config._kw_only_override
        assert False is _config.get_kw_only_override()

    def test_set_kw_only_override(self):
        """
        Sets `_kw_only_override`.
        """
        _config.set_kw_only_override(True)
        assert True is _config._kw_only_override
        _config.set_kw_only_override(False)
        assert False is _config._kw_only_override

    def test_get_kw_only_override(self):
        """
        Returns `_kw_only_override`.
        """
        _config._kw_only_override = True
        assert _config._kw_only_override is _config.get_kw_only_override()
        _config._kw_only_override = False
        assert _config._kw_only_override is _config.get_kw_only_override()

    def test_wrong_type(self):
        """
        Passing anything else than a boolean raises TypeError.
        """
        with pytest.raises(TypeError) as e:
            _config.set_kw_only_override("True")
        assert "'override' must be bool." == e.value.args[0]

    def test_public_namespaces(self):
        """
        The switch is importable from both the attr and the attrs
        namespaces.
        """
        import attr
        import attrs

        assert attr.set_kw_only_override is _config.set_kw_only_override
        assert attr.get_kw_only_override is _config.get_kw_only_override
        assert attrs.set_kw_only_override is _config.set_kw_only_override
        assert attrs.get_kw_only_override is _config.get_kw_only_override
