from itertools import combinations

from src.domain.constants.type_effectiveness import (
    NORMAL_EFFECTIVENESS,
    TYPE_EFFECTIVENESS,
)
from src.domain.value_objects.types import Type


class TypeEffectivenessService:
    """Domain service for type effectiveness calculations.

    Encapsulates business logic for determining damage multipliers based on
    attacking and defending Pokemon types.
    """

    @staticmethod
    def get_effectiveness_multiplier(*, attacker_type: Type, defender_type: Type) -> float:
        """Calculate the type effectiveness multiplier for an attack.

        Args:
            attacker_type: The type of the attacking move
            defender_type: The type of the defending Pokemon

        Returns:
            The damage multiplier:
            - 1.6 for super effective attacks
            - 0.625 for not very effective attacks
            - 0.390625 for no effect attacks
            - 1.0 for normal effectiveness
        """
        return TYPE_EFFECTIVENESS.get((attacker_type, defender_type), NORMAL_EFFECTIVENESS)

    @staticmethod
    def get_most_effective_types(*, defending_types: list[Type], sorted: bool = True) -> list[tuple[Type, float]]:
        """Find the most effective attacking types against a list of defending types.

        For dual-type Pokemon, calculates combined effectiveness by multiplying
        individual type effectiveness multipliers.

        Args:
            defending_types: List of defending Pokemon types (e.g., [Type.PSYCHIC, Type.GHOST]).
            sorted: Whether to sort the results by effectiveness (highest first).

        Returns:
            List of (attacking_type, combined_multiplier) tuples sorted by effectiveness
            (highest first). Only includes types with effectiveness > 1.0.
            Returns empty list if no effective types found.

        Raises:
            ValueError: If defending types is not a list of 1 or 2 types.

        Examples:
            defending_types=[Type.PSYCHIC, Type.GHOST] -> [(Type.DARK, 2.56), (Type.GHOST, 2.56)]
            defending_types=[Type.DRAGON, Type.FLYING] -> [(Type.ICE, 2.56), (Type.DRAGON, 1.6), ...]
        """
        if not defending_types or len(defending_types) > 2:
            raise ValueError("Defending types must be a list of 1 or 2 types.")

        unique_defending_types = set(defending_types)
        effective_types: list[tuple[Type, float]] = []

        for attacking_type in Type:
            combined_multiplier = 1.0
            for defending_type in unique_defending_types:
                combined_multiplier *= TypeEffectivenessService.get_effectiveness_multiplier(
                    attacker_type=attacking_type, defender_type=defending_type
                )
            if combined_multiplier > NORMAL_EFFECTIVENESS:
                effective_types.append((attacking_type, combined_multiplier))

        if sorted:
            effective_types.sort(key=lambda x: x[1], reverse=True)
        return effective_types

    @staticmethod
    def get_best_resistance_combinations(
        *, attacking_type: Type, sorted: bool = True
    ) -> list[tuple[tuple[Type, ...], float]]:
        """Find the best single and dual-type combinations that resist a given attacking type.

        Args:
            attacking_type: The type of the attacking move to find resistances against.
            sorted: Whether to sort results by resistance (best resistance first).

        Returns:
            List of (type_combination, resistance_multiplier) tuples where:
            - type_combination is a tuple like (Type.FAIRY,) or (Type.FAIRY, Type.STEEL)
            - resistance_multiplier is the combined damage multiplier
            Lower multipliers = better resistance. Sorted by resistance if sorted=True.

        Examples:
            attacking_type=Type.DRAGON -> [((Type.FAIRY, Type.STEEL), 0.244140625), ((Type.FAIRY,), 0.390625), ...]
        """
        # Calculate single type resistances.
        resistance_combinations: list[tuple[tuple[Type, ...], float]] = [
            ((defending_type,), resistance_multiplier)
            for defending_type in Type
            if (
                resistance_multiplier := TypeEffectivenessService.get_effectiveness_multiplier(
                    attacker_type=attacking_type,
                    defender_type=defending_type,
                )
            )
            < NORMAL_EFFECTIVENESS
        ]
        # Calculate dual type resistances.
        resistance_combinations.extend(
            [
                (type_tuple1[0] + type_tuple2[0], type_tuple1[1] * type_tuple2[1])
                for type_tuple1, type_tuple2 in combinations(resistance_combinations, 2)
            ]
        )

        if sorted:
            resistance_combinations.sort(key=lambda x: x[1])
        return resistance_combinations
