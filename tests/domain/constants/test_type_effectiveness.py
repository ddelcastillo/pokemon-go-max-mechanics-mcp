from src.domain.constants.type_effectiveness import (
    NO_EFFECT,
    NORMAL_EFFECTIVENESS,
    NOT_VERY_EFFECTIVE,
    SUPER_EFFECTIVE,
    TYPE_EFFECTIVENESS,
)
from src.domain.services.type_effectiveness_service import TypeEffectivenessService
from src.domain.value_objects.types import Type


class TestTypeEffectiveness:
    """Test type effectiveness calculations."""

    def test_super_effective_examples(self) -> None:
        """Test super effective type matchups return 1.6."""
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(attacker_type=Type.WATER, defender_type=Type.FIRE)
            == SUPER_EFFECTIVE
        )
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(attacker_type=Type.FIRE, defender_type=Type.GRASS)
            == SUPER_EFFECTIVE
        )
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(
                attacker_type=Type.ELECTRIC, defender_type=Type.WATER
            )
            == SUPER_EFFECTIVE
        )

    def test_not_very_effective_examples(self) -> None:
        """Test not very effective type matchups return 0.625."""
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(attacker_type=Type.FIRE, defender_type=Type.WATER)
            == NOT_VERY_EFFECTIVE
        )
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(attacker_type=Type.WATER, defender_type=Type.GRASS)
            == NOT_VERY_EFFECTIVE
        )
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(
                attacker_type=Type.ELECTRIC, defender_type=Type.ELECTRIC
            )
            == NOT_VERY_EFFECTIVE
        )

    def test_no_effect_examples(self) -> None:
        """Test no effect type matchups return 0.390625."""
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(attacker_type=Type.NORMAL, defender_type=Type.GHOST)
            == NO_EFFECT
        )
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(
                attacker_type=Type.ELECTRIC, defender_type=Type.GROUND
            )
            == NO_EFFECT
        )
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(
                attacker_type=Type.FIGHTING, defender_type=Type.GHOST
            )
            == NO_EFFECT
        )

    def test_normal_effectiveness_default(self) -> None:
        """Test that unlisted combinations return normal effectiveness (1.0)."""
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(attacker_type=Type.NORMAL, defender_type=Type.NORMAL)
            == NORMAL_EFFECTIVENESS
        )
        assert (
            TypeEffectivenessService.get_effectiveness_multiplier(attacker_type=Type.ELECTRIC, defender_type=Type.FIRE)
            == NORMAL_EFFECTIVENESS
        )

    def test_pokemon_go_specific_values(self) -> None:
        """Test that values match Pokemon Go mechanics (not main series)."""
        assert SUPER_EFFECTIVE == 1.6  # Not 2.0 like main series
        assert NOT_VERY_EFFECTIVE == 0.625  # Not 0.5 like main series
        assert NO_EFFECT == 0.390625  # 0.625^2
        assert NORMAL_EFFECTIVENESS == 1.0

    def test_matrix_structure(self) -> None:
        """Test that the matrix uses tuple keys correctly."""
        sample_key = next(iter(TYPE_EFFECTIVENESS.keys()))
        assert isinstance(sample_key, tuple)
        assert len(sample_key) == 2
        assert isinstance(sample_key[0], Type)
        assert isinstance(sample_key[1], Type)

    def test_symmetric_relationships_exist(self) -> None:
        """Test that some key symmetric relationships are properly defined."""
        assert (Type.FIRE, Type.WATER) in TYPE_EFFECTIVENESS
        assert (Type.WATER, Type.FIRE) in TYPE_EFFECTIVENESS

        fire_vs_water = TYPE_EFFECTIVENESS[(Type.FIRE, Type.WATER)]
        water_vs_fire = TYPE_EFFECTIVENESS[(Type.WATER, Type.FIRE)]

        assert fire_vs_water == NOT_VERY_EFFECTIVE
        assert water_vs_fire == SUPER_EFFECTIVE
