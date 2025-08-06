from src.domain.constants.combat_power_multiplier import COMBAT_POWER_MULTIPLIER


class CombatPowerMultiplierService:
    """Service for retrieving Combat Power Multiplier values by level."""

    @staticmethod
    def get_cpm_by_level(*, level: float) -> float:
        """Get the Combat Power Multiplier value for a given level.

        Args:
            level: The Pokemon level.

        Returns:
            The Combat Power Multiplier value for the given level.

        Raises:
            ValueError: If the level is not found in the CPM mapping.
        """
        if level not in COMBAT_POWER_MULTIPLIER:
            raise ValueError(
                f"Invalid level: {level}. Level must be between 1.0 and "
                f"{float(len(COMBAT_POWER_MULTIPLIER) // 2) + 1}."
            )

        return COMBAT_POWER_MULTIPLIER[level]
