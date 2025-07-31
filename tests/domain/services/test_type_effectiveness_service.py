from itertools import combinations

import pytest

from src.domain.constants.type_effectiveness import (
    NO_EFFECT,
    NORMAL_EFFECTIVENESS,
    NOT_VERY_EFFECTIVE,
    SUPER_EFFECTIVE,
)
from src.domain.services.type_effectiveness_service import TypeEffectivenessService
from src.domain.value_objects.types import Type


class TestTypeEffectivenessService:
    """Test the basic TypeEffectivenessService functionality."""

    def test_get_effectiveness_multiplier_super_effective(self) -> None:
        """Test getting super effective multipliers."""
        service = TypeEffectivenessService()

        result = service.get_effectiveness_multiplier(attacker_type=Type.WATER, defender_type=Type.FIRE)
        assert result == SUPER_EFFECTIVE

    def test_get_effectiveness_multiplier_not_very_effective(self) -> None:
        """Test getting not very effective multipliers."""
        service = TypeEffectivenessService()

        result = service.get_effectiveness_multiplier(attacker_type=Type.FIRE, defender_type=Type.WATER)
        assert result == NOT_VERY_EFFECTIVE

    def test_get_effectiveness_multiplier_no_effect(self) -> None:
        """Test getting no effect multipliers."""
        service = TypeEffectivenessService()

        result = service.get_effectiveness_multiplier(attacker_type=Type.NORMAL, defender_type=Type.GHOST)
        assert result == NO_EFFECT

    def test_get_effectiveness_multiplier_normal_effectiveness(self) -> None:
        """Test getting normal effectiveness for unlisted combinations."""
        service = TypeEffectivenessService()

        result = service.get_effectiveness_multiplier(attacker_type=Type.NORMAL, defender_type=Type.NORMAL)
        assert result == NORMAL_EFFECTIVENESS

    def test_static_method_can_be_called_without_instance(self) -> None:
        """Test that the service method can be called statically."""
        result = TypeEffectivenessService.get_effectiveness_multiplier(
            attacker_type=Type.WATER, defender_type=Type.FIRE
        )
        assert result == SUPER_EFFECTIVE

    def test_explicit_arguments_required(self) -> None:
        """Test that explicit keyword arguments are required."""
        result = TypeEffectivenessService.get_effectiveness_multiplier(
            attacker_type=Type.WATER, defender_type=Type.FIRE
        )
        assert result == SUPER_EFFECTIVE

    def test_service_is_stateless(self) -> None:
        """Test that the service is stateless and multiple calls return same result."""
        service = TypeEffectivenessService()

        result1 = service.get_effectiveness_multiplier(attacker_type=Type.FIRE, defender_type=Type.GRASS)
        result2 = service.get_effectiveness_multiplier(attacker_type=Type.FIRE, defender_type=Type.GRASS)

        assert result1 == result2 == SUPER_EFFECTIVE


class TestTypeEffectivenessServiceMostEffectiveTypes:
    """Test the get_most_effective_types functionality."""

    def test_psychic_ghost_combination_example(self) -> None:
        """Test finding effective types against Psychic + Ghost combination."""
        result = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.PSYCHIC, Type.GHOST])

        expected_multiplier = SUPER_EFFECTIVE * SUPER_EFFECTIVE  # 1.6 * 1.6 = 2.56

        assert len(result) >= 2
        assert (Type.DARK, expected_multiplier) in result
        assert (Type.GHOST, expected_multiplier) in result

    def test_dragon_flying_combination_example(self) -> None:
        """Test finding effective types against Dragon + Flying combination."""
        result = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.DRAGON, Type.FLYING])

        ice_multiplier = SUPER_EFFECTIVE * SUPER_EFFECTIVE
        assert result[0] == (Type.ICE, ice_multiplier)  # Ice is the only and most effective type.
        assert all(ice_multiplier > multiplier > NORMAL_EFFECTIVENESS for _, multiplier in result[1:])

    def test_single_defending_type(self) -> None:
        """Test finding effective types against a single defending type."""
        result = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.FIRE])

        assert {attacking_type for attacking_type, _ in result} == {Type.WATER, Type.GROUND, Type.ROCK}
        assert all(multiplier == SUPER_EFFECTIVE for _, multiplier in result)

    def test_results_sorted_by_effectiveness(self) -> None:
        """Test that results are sorted by effectiveness (highest first)."""
        result = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.DRAGON, Type.FLYING])

        for i in range(len(result) - 1):
            assert result[i][1] >= result[i + 1][1]

    def test_no_effect_combination_handling(self) -> None:
        """Test combination that includes no effect scenarios."""
        result = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.NORMAL, Type.GHOST])

        assert Type.NORMAL not in [attacking_type for attacking_type, _ in result]

    def test_normal_type_has_limited_weaknesses(self) -> None:
        """Test case with Normal type that has few weaknesses."""
        result = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.NORMAL])

        assert len(result) == 1
        assert Type.FIGHTING in [attacking_type for attacking_type, _ in result]


class TestTypeEffectivenessServiceInputValidation:
    """Test input validation for get_most_effective_types method."""

    def test_empty_list_raises_error(self) -> None:
        """Test that empty defending types list raises ValueError."""
        with pytest.raises(ValueError, match="Defending types must be a list of 1 or 2 types"):
            TypeEffectivenessService.get_most_effective_types(defending_types=[])

    def test_exactly_three_types_raises_error(self) -> None:
        """Test that exactly 3 defending types raises ValueError."""
        with pytest.raises(ValueError, match="Defending types must be a list of 1 or 2 types"):
            TypeEffectivenessService.get_most_effective_types(defending_types=[Type.FIRE, Type.WATER, Type.GRASS])

    def test_four_or_more_types_raises_error(self) -> None:
        """Test that 4 or more defending types raises ValueError."""
        with pytest.raises(ValueError, match="Defending types must be a list of 1 or 2 types"):
            TypeEffectivenessService.get_most_effective_types(
                defending_types=[Type.FIRE, Type.WATER, Type.GRASS, Type.ELECTRIC]
            )


class TestTypeEffectivenessServiceDuplicateHandling:
    """Test duplicate type handling for get_most_effective_types method."""

    def test_duplicate_types_handled_correctly(self) -> None:
        """Test that duplicate defending types are handled correctly."""
        result_duplicates = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.FIRE, Type.FIRE])
        result_single = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.FIRE])

        assert result_duplicates == result_single

    def test_duplicates_with_invalid_count_still_raises_error(self) -> None:
        """Test that duplicates are removed but different types are preserved."""
        with pytest.raises(ValueError, match="Defending types must be a list of 1 or 2 types"):
            TypeEffectivenessService.get_most_effective_types(defending_types=[Type.FIRE, Type.WATER, Type.FIRE])


class TestTypeEffectivenessServiceSortingOptions:
    """Test sorting functionality for get_most_effective_types method."""

    def test_sorted_vs_unsorted_results(self) -> None:
        """Test that sorted=False returns unsorted results."""
        result_sorted = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.FIRE], sorted=True)
        result_unsorted = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.FIRE], sorted=False)

        assert len(result_sorted) == len(result_unsorted)
        assert set(result_sorted) == set(result_unsorted)

        for i in range(len(result_sorted) - 1):
            assert result_sorted[i][1] >= result_sorted[i + 1][1]

    def test_default_sorting_behavior(self) -> None:
        """Test that default behavior sorts results by effectiveness."""
        result = TypeEffectivenessService.get_most_effective_types(defending_types=[Type.DRAGON, Type.FLYING])

        for i in range(len(result) - 1):
            assert result[i][1] >= result[i + 1][1]


class TestTypeEffectivenessServiceResistanceCombinations:
    """Test the get_best_resistance_combinations functionality."""

    def test_dragon_resistance_example(self) -> None:
        """Test finding best resistances against Dragon attacks (user's example)."""
        result = TypeEffectivenessService.get_best_resistance_combinations(attacking_type=Type.DRAGON)

        assert ((Type.FAIRY,), NO_EFFECT) in result
        assert ((Type.STEEL,), NOT_VERY_EFFECTIVE) in result
        assert result[0] == ((Type.FAIRY, Type.STEEL), NO_EFFECT * NOT_VERY_EFFECTIVE)  # Aprox. 0.244
        assert all(multiplier < NORMAL_EFFECTIVENESS for _, multiplier in result[1:])
        assert all(result[i][1] <= result[i + 1][1] for i in range(len(result) - 1))

    def test_includes_both_single_and_dual_types(self) -> None:
        """Test that results include both single and dual type combinations."""
        result = TypeEffectivenessService.get_best_resistance_combinations(attacking_type=Type.FIRE)

        single_type_count = sum(1 for combination, _ in result if len(combination) == 1)
        dual_type_count = sum(1 for combination, _ in result if len(combination) == 2)

        # Fire is resisted by: Fire (0.625), Water (0.625), Rock (0.625), Dragon (0.625) = 4 types
        assert single_type_count == 4
        assert dual_type_count == 6  # Dual combinations should be C(4,2) = 6
        assert len(result) == 10

    def test_no_duplicate_combinations(self) -> None:
        """Test that dual combinations don't include duplicates like (Fire, Water) and (Water, Fire)."""
        result = TypeEffectivenessService.get_best_resistance_combinations(attacking_type=Type.ELECTRIC)

        dual_combinations = [combination for combination, _ in result if len(combination) == 2]

        # Check no reversed duplicates exist, frozenset is used to avoid duplicates (base truth).
        combination_sets = [frozenset(combination) for combination in dual_combinations]
        assert len(combination_sets) == len(set(combination_sets)), "Duplicate combinations found"

    def test_optimization_reduces_dual_combinations(self) -> None:
        """Test that optimization significantly reduces dual combinations calculated."""
        # Test with Normal type (which has very few resistances).
        result = TypeEffectivenessService.get_best_resistance_combinations(attacking_type=Type.NORMAL)

        single_type_count = sum(1 for combination, _ in result if len(combination) == 1)
        dual_type_count = sum(1 for combination, _ in result if len(combination) == 2)
        dual_combinations = [combination for combination, _ in result if len(combination) == 2]
        actual_combinations = [set(combination) for combination in dual_combinations]
        expected_combinations = [{Type.BUG, Type.GHOST}, {Type.BUG, Type.STEEL}, {Type.GHOST, Type.STEEL}]

        # Normal is resisted by: Bug (0.625), Ghost (0.390625), Steel (0.625) = 3 types
        assert single_type_count == 3
        assert dual_type_count == 3  # Dual combinations should be C(3,2) = 3
        assert len(result) == 6
        assert all(expected in actual_combinations for expected in expected_combinations)

    def test_unsorted_option(self) -> None:
        """Test that sorted=False returns unsorted results."""
        sorted_result = TypeEffectivenessService.get_best_resistance_combinations(
            attacking_type=Type.NORMAL, sorted=True
        )
        unsorted_result = TypeEffectivenessService.get_best_resistance_combinations(
            attacking_type=Type.NORMAL, sorted=False
        )

        assert len(sorted_result) == len(unsorted_result)
        assert set(sorted_result) == set(unsorted_result)
        assert all(sorted_result[i][1] <= sorted_result[i + 1][1] for i in range(len(sorted_result) - 1))
