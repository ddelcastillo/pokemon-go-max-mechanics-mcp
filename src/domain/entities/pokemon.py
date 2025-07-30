from dataclasses import dataclass

from src.domain.entities.move import Move
from src.domain.value_objects.generation import Generation
from src.domain.value_objects.types import Type


@dataclass
class Pokemon:
    """Represents a Pokemon entity with its core attributes.

    A Pokemon is characterized by its identity (name, dex number), typing,
    generation, base stats (attack, defense, stamina), and available moves
    for battle mechanics.

    Attributes:
        name: The Pokemon's species name.
        dex_number: National Pokedex number (must be positive).
        types: List of 1-2 Pokemon types.
        generation: The generation this Pokemon was introduced.
        attack: Base attack stat (must be positive).
        defense: Base defense stat (must be positive).
        stamina: Base stamina/HP stat (must be positive).
        quick_moves: Available quick moves for battle.
        charge_moves: Available charge moves for battle.
    """

    name: str
    dex_number: int
    types: list[Type]
    generation: Generation
    attack: int
    defense: int
    stamina: int
    quick_moves: list[Move]
    charge_moves: list[Move]

    def __post_init__(self) -> None:
        """Validate Pokemon attributes."""
        if not (1 <= len(self.types) <= 2):
            raise ValueError("A Pokemon must have exactly 1 or 2 types.")
        if self.dex_number <= 0:
            raise ValueError("dex_number must be greater than 0.")
        if self.generation not in Generation:
            raise ValueError("generation must be a valid Generation.")
        if self.attack <= 0:
            raise ValueError("attack must be greater than 0.")
        if self.defense <= 0:
            raise ValueError("defense must be greater than 0.")
        if self.stamina <= 0:
            raise ValueError("stamina must be greater than 0.")
