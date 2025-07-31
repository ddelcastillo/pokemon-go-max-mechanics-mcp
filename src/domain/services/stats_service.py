class StatsService:
    """Service for calculating Pokemon stats."""

    @staticmethod
    def calculate_attack(*, base_attack: int, attack_iv: int, cpm: float) -> float:
        """Calculate the effective attack stat for a Pokemon.

        Args:
            base_attack: The base attack stat of the Pokemon species.
            attack_iv: The individual value for attack (0-15).
            cpm: The Combat Power Multiplier for the Pokemon's level.

        Returns:
            The calculated attack stat.
        """
        return (base_attack + attack_iv) * cpm

    @staticmethod
    def calculate_defense(*, base_defense: int, defense_iv: int, cpm: float) -> float:
        """Calculate the effective defense stat for a Pokemon.

        Args:
            base_defense: The base defense stat of the Pokemon species.
            defense_iv: The individual value for defense (0-15).
            cpm: The Combat Power Multiplier for the Pokemon's level.

        Returns:
            The calculated defense stat.
        """
        return (base_defense + defense_iv) * cpm

    @staticmethod
    def calculate_stamina(*, base_stamina: int, stamina_iv: int, cpm: float) -> int:
        """Calculate the effective stamina (HP) stat for a Pokemon.

        Args:
            base_stamina: The base stamina stat of the Pokemon species.
            stamina_iv: The individual value for stamina (0-15).
            cpm: The Combat Power Multiplier for the Pokemon's level.

        Returns:
            The calculated stamina stat (rounded down to integer).
        """
        return int((base_stamina + stamina_iv) * cpm)
