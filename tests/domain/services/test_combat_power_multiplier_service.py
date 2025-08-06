import pytest

from src.domain.services.combat_power_multiplier import CombatPowerMultiplierService


class TestCombatPowerMultiplierService:
    """Test Combat Power Multiplier Service."""

    def test_get_cpm_by_level_valid_levels(self) -> None:
        """Test getting CPM values for valid levels."""
        assert CombatPowerMultiplierService.get_cpm_by_level(level=1.0) == 0.094
        assert CombatPowerMultiplierService.get_cpm_by_level(level=20.0) == 0.5974
        assert CombatPowerMultiplierService.get_cpm_by_level(level=51.0) == 0.8453

    def test_get_cpm_by_level_invalid_level(self) -> None:
        """Test that invalid levels raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            CombatPowerMultiplierService.get_cpm_by_level(level=0.5)

        assert "Invalid level: 0.5" in str(exc_info.value)

        with pytest.raises(ValueError):
            CombatPowerMultiplierService.get_cpm_by_level(level=56.0)
