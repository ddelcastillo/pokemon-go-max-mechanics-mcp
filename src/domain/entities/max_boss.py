from dataclasses import dataclass

from src.domain.entities.pokemon import Pokemon
from src.domain.value_objects.tier import Tier


@dataclass
class MaxBoss:
    """Represents a Max Boss entity with its core attributes.

    Attributes:
        base_pokemon: The underlying Pokemon that serves as the base for this Max Boss.
        atk_cpm: Attack Combat Power Multiplier for this Max Boss.
        def_cpm: Defense Combat Power Multiplier for this Max Boss.
        hp: Hit Points (health) of this Max Boss.
        tier: The difficulty tier of this Max Boss (T1-T6).
    """

    base_pokemon: Pokemon
    atk_cpm: float
    def_cpm: float
    hp: int
    tier: Tier

    def __post_init__(self) -> None:
        """Validate Max Boss attributes."""
        if self.atk_cpm <= 0:
            raise ValueError("Attack Combat Power Multiplier must be positive.")
        if self.def_cpm <= 0:
            raise ValueError("Defense Combat Power Multiplier must be positive.")
        if self.hp <= 0:
            raise ValueError("Hit Points must be positive.")
        if self.tier not in Tier:
            raise ValueError(f"Invalid tier: {self.tier}.")
