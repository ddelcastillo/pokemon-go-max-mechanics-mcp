import pytest

from src.domain.entities.move import Move
from src.domain.entities.pokemon import Pokemon
from src.domain.value_objects.generation import Generation
from src.domain.value_objects.types import Type


class TestPokemon:
    """Test suite for Pokemon entity, focusing on domain invariants and business rules."""

    @pytest.fixture
    def sample_moves(self) -> dict[str, list[Move]]:
        """Fixture providing sample moves for testing."""
        quick_moves = [
            Move(internal_id="QUICK_ATTACK", name="Quick Attack", power=8, energy=10, duration=1500, type=Type.NORMAL),
            Move(
                internal_id="THUNDERBOLT", name="Thunderbolt", power=12, energy=16, duration=1100, type=Type.ELECTRIC
            ),
        ]

        charge_moves = [
            Move(internal_id="BODY_SLAM", name="Body Slam", power=60, energy=35, duration=1900, type=Type.NORMAL),
            Move(internal_id="THUNDER", name="Thunder", power=100, energy=60, duration=2400, type=Type.ELECTRIC),
        ]

        return {"quick": quick_moves, "charge": charge_moves}

    def test_pokemon_creation_with_valid_single_type(self, sample_moves: dict[str, list[Move]]) -> None:
        """Test creating a Pokemon with a single type and valid attributes."""
        pokemon = Pokemon(
            name="Pikachu",
            dex_number=25,
            types=[Type.ELECTRIC],
            generation=Generation.KANTO,
            attack=112,
            defense=96,
            stamina=111,
            quick_moves=sample_moves["quick"],
            charge_moves=sample_moves["charge"],
        )

        assert pokemon.name == "Pikachu"
        assert pokemon.dex_number == 25
        assert pokemon.types == [Type.ELECTRIC]
        assert pokemon.generation == Generation.KANTO
        assert pokemon.attack == 112
        assert pokemon.defense == 96
        assert pokemon.stamina == 111
        assert len(pokemon.quick_moves) == 2
        assert len(pokemon.charge_moves) == 2

    def test_pokemon_creation_with_valid_dual_type(self, sample_moves: dict[str, list[Move]]) -> None:
        """Test creating a Pokemon with dual types."""
        pokemon = Pokemon(
            name="Charizard",
            dex_number=6,
            types=[Type.FIRE, Type.FLYING],
            generation=Generation.KANTO,
            attack=223,
            defense=173,
            stamina=186,
            quick_moves=sample_moves["quick"],
            charge_moves=sample_moves["charge"],
        )

        assert pokemon.types == [Type.FIRE, Type.FLYING]
        assert len(pokemon.types) == 2

    @pytest.mark.parametrize(
        "pokemon_data,expected_error",
        [
            # Empty types
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": 100,
                    "stamina": 100,
                },
                "A Pokemon must have exactly 1 or 2 types",
            ),
            # Too many types
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [Type.FIRE, Type.WATER, Type.ELECTRIC],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": 100,
                    "stamina": 100,
                },
                "A Pokemon must have exactly 1 or 2 types",
            ),
            # Zero dex number
            (
                {
                    "name": "Invalid",
                    "dex_number": 0,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": 100,
                    "stamina": 100,
                },
                "dex_number must be greater than 0",
            ),
            # Negative dex number
            (
                {
                    "name": "Invalid",
                    "dex_number": -1,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": 100,
                    "stamina": 100,
                },
                "dex_number must be greater than 0",
            ),
            # Zero attack
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": 0,
                    "defense": 100,
                    "stamina": 100,
                },
                "attack must be greater than 0",
            ),
            # Negative attack
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": -1,
                    "defense": 100,
                    "stamina": 100,
                },
                "attack must be greater than 0",
            ),
            # Zero defense
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": 0,
                    "stamina": 100,
                },
                "defense must be greater than 0",
            ),
            # Negative defense
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": -1,
                    "stamina": 100,
                },
                "defense must be greater than 0",
            ),
            # Zero stamina
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": 100,
                    "stamina": 0,
                },
                "stamina must be greater than 0",
            ),
            # Negative stamina
            (
                {
                    "name": "Invalid",
                    "dex_number": 1,
                    "types": [Type.NORMAL],
                    "generation": Generation.KANTO,
                    "attack": 100,
                    "defense": 100,
                    "stamina": -1,
                },
                "stamina must be greater than 0",
            ),
        ],
    )
    def test_pokemon_creation_with_invalid_data_raises_error(
        self, sample_moves: dict[str, list[Move]], pokemon_data: dict, expected_error: str
    ) -> None:
        """Test that creating a Pokemon with invalid data raises appropriate ValueError."""
        pokemon_data_with_moves = {
            **pokemon_data,
            "quick_moves": sample_moves["quick"],
            "charge_moves": sample_moves["charge"],
        }

        with pytest.raises(ValueError, match=expected_error):
            Pokemon(**pokemon_data_with_moves)

    def test_pokemon_creation_with_empty_move_lists(self) -> None:
        """Test that Pokemon can be created with empty move lists."""
        pokemon = Pokemon(
            name="Ditto",
            dex_number=132,
            types=[Type.NORMAL],
            generation=Generation.KANTO,
            attack=91,
            defense=91,
            stamina=134,
            quick_moves=[],
            charge_moves=[],
        )

        assert pokemon.quick_moves == []
        assert pokemon.charge_moves == []

    def test_pokemon_minimum_valid_stat_values(self, sample_moves: dict[str, list[Move]]) -> None:
        """Test Pokemon with minimum valid stat values (boundary testing)."""
        pokemon = Pokemon(
            name="Weak",
            dex_number=1,
            types=[Type.BUG],
            generation=Generation.KANTO,
            attack=1,
            defense=1,
            stamina=1,
            quick_moves=sample_moves["quick"],
            charge_moves=sample_moves["charge"],
        )

        assert pokemon.attack == 1
        assert pokemon.defense == 1
        assert pokemon.stamina == 1
