import pytest

from src.domain.entities.max_pokemon import MaxPokemon
from src.domain.entities.move import Move
from src.domain.entities.pokemon import Pokemon
from src.domain.value_objects.generation import Generation
from src.domain.value_objects.types import Type


class TestMaxPokemon:
    """Test suite for MaxPokemon entity, focusing on domain invariants and business rules."""

    @pytest.fixture
    def sample_pokemon(self) -> Pokemon:
        """Fixture providing a sample Pokemon for testing."""
        sample_move = Move(
            internal_id="QUICK_ATTACK",
            name="Quick Attack",
            power=8,
            energy=10,
            duration=1500,
            type=Type.NORMAL,
        )
        return Pokemon(
            name="Charizard",
            dex_number=6,
            types=[Type.FIRE, Type.FLYING],
            generation=Generation.KANTO,
            attack=223,
            defense=173,
            stamina=186,
            quick_moves=[sample_move],
            charge_moves=[sample_move],
        )

    @pytest.fixture
    def sample_gigantamax_move(self) -> Move:
        """Fixture providing a sample Gigantamax move for testing."""
        return Move(
            internal_id="G_MAX_WILDFIRE",
            name="G-Max Wildfire",
            power=150,
            energy=100,
            duration=3000,
            type=Type.FIRE,
        )

    def test_max_pokemon_creation_not_gigantamax(self, sample_pokemon: Pokemon) -> None:
        """Test creating a MaxPokemon that is not in Gigantamax form."""
        max_pokemon = MaxPokemon(
            base_pokemon=sample_pokemon,
            is_gigantamax=False,
            is_gigantamax_available=False,
        )

        assert max_pokemon.base_pokemon == sample_pokemon
        assert max_pokemon.is_gigantamax is False
        assert max_pokemon.is_gigantamax_available is False
        assert max_pokemon.gigantamax_move is None

    def test_max_pokemon_creation_gigantamax_with_move(
        self, sample_pokemon: Pokemon, sample_gigantamax_move: Move
    ) -> None:
        """Test creating a MaxPokemon in Gigantamax form with a move."""
        max_pokemon = MaxPokemon(
            base_pokemon=sample_pokemon,
            is_gigantamax=True,
            is_gigantamax_available=True,
            gigantamax_move=sample_gigantamax_move,
        )

        assert max_pokemon.base_pokemon == sample_pokemon
        assert max_pokemon.is_gigantamax is True
        assert max_pokemon.is_gigantamax_available is True
        assert max_pokemon.gigantamax_move == sample_gigantamax_move

    def test_max_pokemon_gigantamax_available_but_not_active(self, sample_pokemon: Pokemon) -> None:
        """Test creating a MaxPokemon where Gigantamax is available but not active."""
        with pytest.raises(ValueError, match="Gigantamax is not available for this Pokemon."):
            MaxPokemon(
                base_pokemon=sample_pokemon,
                is_gigantamax=False,
                is_gigantamax_available=True,
            )

    def test_max_pokemon_gigantamax_without_move(self, sample_pokemon: Pokemon) -> None:
        """Test that Gigantamax form requires a move."""
        with pytest.raises(ValueError, match="Gigantamax move is required when in Gigantamax form."):
            MaxPokemon(
                base_pokemon=sample_pokemon,
                is_gigantamax=True,
                is_gigantamax_available=True,
                gigantamax_move=None,
            )

    @pytest.mark.parametrize(
        "is_gigantamax,is_gigantamax_available,gigantamax_move_present,should_raise",
        [
            # Valid combinations
            (False, False, False, False),  # Normal Pokemon, no Gigantamax
            (True, True, True, False),  # Gigantamax active with move
            # Invalid combinations
            (False, True, False, True),  # Available but not active - should raise
            (True, True, False, True),  # Active but no move - should raise
        ],
    )
    def test_max_pokemon_validation_combinations(
        self,
        sample_pokemon: Pokemon,
        sample_gigantamax_move: Move,
        is_gigantamax: bool,
        is_gigantamax_available: bool,
        gigantamax_move_present: bool,
        should_raise: bool,
    ) -> None:
        """Test various combinations of Gigantamax settings for validation."""
        gigantamax_move = sample_gigantamax_move if gigantamax_move_present else None

        if should_raise:
            with pytest.raises(ValueError):
                MaxPokemon(
                    base_pokemon=sample_pokemon,
                    is_gigantamax=is_gigantamax,
                    is_gigantamax_available=is_gigantamax_available,
                    gigantamax_move=gigantamax_move,
                )
        else:
            max_pokemon = MaxPokemon(
                base_pokemon=sample_pokemon,
                is_gigantamax=is_gigantamax,
                is_gigantamax_available=is_gigantamax_available,
                gigantamax_move=gigantamax_move,
            )
            assert max_pokemon.is_gigantamax == is_gigantamax
            assert max_pokemon.is_gigantamax_available == is_gigantamax_available

    def test_max_pokemon_gigantamax_move_optional_when_not_gigantamax(self, sample_pokemon: Pokemon) -> None:
        """Test that gigantamax_move can be None when not in Gigantamax form."""
        max_pokemon = MaxPokemon(
            base_pokemon=sample_pokemon,
            is_gigantamax=False,
            is_gigantamax_available=False,
            gigantamax_move=None,
        )

        assert max_pokemon.gigantamax_move is None
