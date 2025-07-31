import pytest

from src.domain.entities.max_boss import MaxBoss
from src.domain.entities.move import Move
from src.domain.entities.pokemon import Pokemon
from src.domain.value_objects.generation import Generation
from src.domain.value_objects.tier import Tier
from src.domain.value_objects.types import Type


class TestMaxBoss:
    """Test suite for MaxBoss entity, focusing on domain invariants and business rules."""

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
            name="Pikachu",
            dex_number=25,
            types=[Type.ELECTRIC],
            generation=Generation.KANTO,
            attack=112,
            defense=96,
            stamina=111,
            quick_moves=[sample_move],
            charge_moves=[sample_move],
        )

    def test_max_boss_creation_with_valid_data(self, sample_pokemon: Pokemon) -> None:
        """Test creating a MaxBoss with valid attributes."""
        max_boss = MaxBoss(
            base_pokemon=sample_pokemon,
            atk_cpm=2.5,
            def_cpm=1.8,
            hp=15000,
            tier=Tier.TIER_3,
        )

        assert max_boss.base_pokemon == sample_pokemon
        assert max_boss.atk_cpm == 2.5
        assert max_boss.def_cpm == 1.8
        assert max_boss.hp == 15000
        assert max_boss.tier == Tier.TIER_3

    @pytest.mark.parametrize("tier", [Tier.TIER_1, Tier.TIER_2, Tier.TIER_3, Tier.TIER_4, Tier.TIER_5, Tier.TIER_6])
    def test_max_boss_creation_with_all_valid_tiers(self, sample_pokemon: Pokemon, tier: Tier) -> None:
        """Test creating MaxBoss with all valid tier values."""
        max_boss = MaxBoss(
            base_pokemon=sample_pokemon,
            atk_cpm=1.5,
            def_cpm=1.2,
            hp=10000,
            tier=tier,
        )

        assert max_boss.tier == tier

    @pytest.mark.parametrize(
        "max_boss_data,expected_error",
        [
            # Zero attack CPM
            (
                {
                    "atk_cpm": 0.0,
                    "def_cpm": 1.5,
                    "hp": 10000,
                    "tier": Tier.TIER_1,
                },
                "Attack Combat Power Multiplier must be positive.",
            ),
            # Negative attack CPM
            (
                {
                    "atk_cpm": -1.2,
                    "def_cpm": 1.5,
                    "hp": 10000,
                    "tier": Tier.TIER_1,
                },
                "Attack Combat Power Multiplier must be positive.",
            ),
            # Zero defense CPM
            (
                {
                    "atk_cpm": 2.0,
                    "def_cpm": 0.0,
                    "hp": 10000,
                    "tier": Tier.TIER_1,
                },
                "Defense Combat Power Multiplier must be positive.",
            ),
            # Negative defense CPM
            (
                {
                    "atk_cpm": 2.0,
                    "def_cpm": -0.8,
                    "hp": 10000,
                    "tier": Tier.TIER_1,
                },
                "Defense Combat Power Multiplier must be positive.",
            ),
            # Zero HP
            (
                {
                    "atk_cpm": 2.0,
                    "def_cpm": 1.5,
                    "hp": 0,
                    "tier": Tier.TIER_1,
                },
                "Hit Points must be positive.",
            ),
            # Negative HP
            (
                {
                    "atk_cpm": 2.0,
                    "def_cpm": 1.5,
                    "hp": -5000,
                    "tier": Tier.TIER_1,
                },
                "Hit Points must be positive.",
            ),
        ],
    )
    def test_max_boss_validation_errors(
        self, sample_pokemon: Pokemon, max_boss_data: dict, expected_error: str
    ) -> None:
        """Test that MaxBoss raises appropriate validation errors for invalid data."""
        with pytest.raises(ValueError, match=expected_error):
            MaxBoss(base_pokemon=sample_pokemon, **max_boss_data)

    def test_max_boss_with_boundary_values(self, sample_pokemon: Pokemon) -> None:
        """Test MaxBoss creation with boundary values."""
        max_boss = MaxBoss(
            base_pokemon=sample_pokemon,
            atk_cpm=0.1,  # Very small positive value
            def_cpm=0.1,  # Very small positive value
            hp=1,  # Minimum positive HP
            tier=Tier.TIER_1,
        )

        assert max_boss.atk_cpm == 0.1
        assert max_boss.def_cpm == 0.1
        assert max_boss.hp == 1
