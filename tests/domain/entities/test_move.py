import pytest

from src.domain.entities.move import Move
from src.domain.value_objects.types import Type


class TestMove:
    """Test suite for Move entity."""

    @pytest.mark.parametrize(
        "energy",
        [-50, 55],
    )
    def test_move_creation_with_valid_data(self, energy: int) -> None:
        """Test that a Move can be created with valid attributes and any integer energy value."""
        move = Move(
            internal_id="THUNDERBOLT",
            name="Thunderbolt",
            power=90,
            energy=energy,
            duration=2500,
            type=Type.ELECTRIC,
        )

        assert move.internal_id == "THUNDERBOLT"
        assert move.name == "Thunderbolt"
        assert move.power == 90
        assert move.energy == energy
        assert move.duration == 2500
        assert move.type == Type.ELECTRIC

    @pytest.mark.parametrize(
        "move_data,expected_error",
        [
            # Zero power
            (
                {
                    "internal_id": "THUNDER_WAVE",
                    "name": "Thunder Wave",
                    "power": 0,
                    "energy": 45,
                    "duration": 2900,
                    "type": Type.ELECTRIC,
                },
                "power must be greater than 0",
            ),
            # Negative power
            (
                {
                    "internal_id": "SPECIAL_MOVE",
                    "name": "Special Move",
                    "power": -10,
                    "energy": 35,
                    "duration": 1500,
                    "type": Type.NORMAL,
                },
                "power must be greater than 0",
            ),
            # Zero duration
            (
                {
                    "internal_id": "INSTANT_MOVE",
                    "name": "Instant Move",
                    "power": 50,
                    "energy": 25,
                    "duration": 0,
                    "type": Type.NORMAL,
                },
                "duration must be greater than 0",
            ),
            # Negative duration
            (
                {
                    "internal_id": "REVERSE_MOVE",
                    "name": "Reverse Move",
                    "power": 50,
                    "energy": 25,
                    "duration": -100,
                    "type": Type.NORMAL,
                },
                "duration must be greater than 0",
            ),
            # Zero energy
            (
                {
                    "internal_id": "ZERO_ENERGY_MOVE",
                    "name": "Zero Energy Move",
                    "power": 50,
                    "energy": 0,
                    "duration": 1500,
                    "type": Type.NORMAL,
                },
                "energy cannot be zero",
            ),
            # Invalid type
            (
                {
                    "internal_id": "INVALID_MOVE",
                    "name": "Invalid Move",
                    "power": 50,
                    "energy": 25,
                    "duration": 1500,
                    "type": "InvalidType",
                },
                "type must be a valid Type",
            ),
        ],
    )
    def test_move_creation_with_invalid_data_raises_error(self, move_data: dict, expected_error: str) -> None:
        """Test that creating a Move with invalid data raises appropriate ValueError."""
        with pytest.raises(ValueError, match=expected_error):
            Move(**move_data)  # type: ignore

    def test_move_with_negative_energy(self) -> None:
        """Test that a Move can have negative energy (energy generation)."""
        move = Move(
            internal_id="ENERGY_GAIN", name="Energy Gain", power=5, energy=-10, duration=1000, type=Type.NORMAL
        )

        assert move.energy == -10

    def test_move_minimum_valid_values(self) -> None:
        """Test that a Move can have minimum valid power and duration values."""
        move = Move(
            internal_id="MINIMAL_MOVE",
            name="Minimal Move",
            power=1,
            energy=1,
            duration=1,
            type=Type.NORMAL,
        )

        assert move.power == 1
        assert move.energy == 1
        assert move.duration == 1

    def test_move_mutability(self) -> None:
        """Test that Move attributes can be modified (dataclass behavior)."""
        move = Move(
            internal_id="THUNDERBOLT", name="Thunderbolt", power=90, energy=55, duration=2500, type=Type.ELECTRIC
        )

        move.power = 95
        assert move.power == 95

    def test_move_field_metadata(self) -> None:
        """Test that duration field has correct metadata."""
        from dataclasses import fields

        move_fields = fields(Move)
        duration_field = next(field for field in move_fields if field.name == "duration")

        assert duration_field.metadata == {"unit": "milliseconds"}
