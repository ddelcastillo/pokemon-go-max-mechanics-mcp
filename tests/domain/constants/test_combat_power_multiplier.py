from src.domain.constants.combat_power_multiplier import (
    COMBAT_POWER_MULTIPLIER,
    MAX_CPM,
    MIN_CPM,
)


class TestCombatPowerMultiplier:
    """Test Combat Power Multiplier constants."""

    def test_boundary_values(self) -> None:
        """Test minimum and maximum CPM values."""
        assert MIN_CPM == 0.094
        assert MAX_CPM == 0.8653
        assert COMBAT_POWER_MULTIPLIER[1.0] == MIN_CPM
        assert COMBAT_POWER_MULTIPLIER[55.0] == MAX_CPM

    def test_specific_level_mappings(self) -> None:
        """Test specific level to CPM mappings."""
        assert COMBAT_POWER_MULTIPLIER[1.0] == 0.094
        assert COMBAT_POWER_MULTIPLIER[20.0] == 0.5974
        assert COMBAT_POWER_MULTIPLIER[30.0] == 0.7317
        assert COMBAT_POWER_MULTIPLIER[40.0] == 0.7903
        assert COMBAT_POWER_MULTIPLIER[1.5] == 0.13513743215803847
        assert COMBAT_POWER_MULTIPLIER[20.5] == 0.6048236602280411

    def test_level_range_completeness(self) -> None:
        """Test that all levels from 1 to 55 (including half levels) are present."""
        expected_levels: list[float] = [
            sub_level for level in range(1, 55) for sub_level in [float(level), level + 0.5]
        ] + [55.0]
        missing_levels = [level for level in expected_levels if level not in COMBAT_POWER_MULTIPLIER]
        assert all(level in COMBAT_POWER_MULTIPLIER for level in expected_levels), (
            f"Missing levels from CPM mapping: {missing_levels}"
        )
        assert len(COMBAT_POWER_MULTIPLIER) == 109

    def test_monotonic_progression(self) -> None:
        """Test that CPM values increase monotonically with level."""
        sorted_levels = sorted(COMBAT_POWER_MULTIPLIER.keys())
        cpm_values = [COMBAT_POWER_MULTIPLIER[level] for level in sorted_levels]

        assert all(cpm_values[i] > cpm_values[i - 1] for i in range(1, len(cpm_values))), (
            "CPM values should increase monotonically with level"
        )
