from dataclasses import dataclass

from src.domain.entities.move import Move
from src.domain.entities.pokemon import Pokemon


@dataclass
class MaxPokemon:
    """Represents a Max Pokemon entity with its core attributes.

    Attributes:
        base_pokemon: The base Pokemon that this Max Pokemon is based on.
        is_gigantamax: Whether this Pokemon is in Gigantamax form.
        is_gigantamax_available: Whether this Pokemon can enter Gigantamax form.
        gigantamax_move: The move that this Pokemon can use in Gigantamax form.
    """

    base_pokemon: Pokemon
    is_gigantamax: bool
    is_gigantamax_available: bool
    gigantamax_move: Move | None = None

    def __post_init__(self) -> None:
        """Validate Max Pokemon attributes."""
        if self.is_gigantamax_available and not self.is_gigantamax:
            raise ValueError("Gigantamax is not available for this Pokemon.")
        if self.is_gigantamax and not self.gigantamax_move:
            raise ValueError("Gigantamax move is required when in Gigantamax form.")
