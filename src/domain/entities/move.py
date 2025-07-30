from dataclasses import dataclass, field

from src.domain.value_objects.types import Type


@dataclass
class Move:
    """Represents a Pokemon move with its core attributes.

    Attributes:
        internal_id: The unique identifier for the move.
        name: The display name of the move.
        power: The power value of the move (must be > 0).
        energy: The energy value of the move (cannot be zero).
        duration: The duration of the move in milliseconds (must be > 0).
        type: The Pokemon type of the move.
    """

    internal_id: str
    name: str
    power: int
    energy: int
    duration: int = field(metadata={"unit": "milliseconds"})
    type: Type

    def __post_init__(self) -> None:
        """Validate Move attributes."""
        if self.power <= 0:
            raise ValueError("power must be greater than 0.")
        if self.energy == 0:
            raise ValueError("energy cannot be zero.")
        if self.duration <= 0:
            raise ValueError("duration must be greater than 0.")
        if self.type not in Type:
            raise ValueError("type must be a valid Type.")
