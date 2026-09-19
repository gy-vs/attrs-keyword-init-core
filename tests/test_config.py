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

    def test_force_kw_only_override_default(self):
        """
        The historic class-level kw_only override is off by default.
        """
        assert False is _config._force_kw_only_override

    def test_set_force_kw_only_override(self):
        """
        Sets `_force_kw_only_override`.
        """
        _config.set_force_kw_only_override(True)
        assert True is _config._force_kw_only_override
        _config.set_force_kw_only_override(False)
        assert False is _config._force_kw_only_override

    def test_get_force_kw_only_override(self):
        """
        Returns `_force_kw_only_override`.
        """
        _config._force_kw_only_override = True
        assert _config._force_kw_only_override is (
            _config.get_force_kw_only_override()
        )
        _config._force_kw_only_override = False
        assert _config._force_kw_only_override is (
            _config.get_force_kw_only_override()
        )

    def test_force_kw_only_override_wrong_type(self):
        """
        Passing anything else than a boolean raises TypeError.
        """
        with pytest.raises(TypeError) as e:
            _config.set_force_kw_only_override("True")
        assert "'force' must be bool." == e.value.args[0]
