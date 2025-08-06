from math import floor
from typing import Final

from src.domain.constants.battle_mechanics import STAB_MULTIPLIER, WEATHER_MULTIPLIER
from src.domain.entities.move import Move
from src.domain.entities.pokemon import Pokemon
from src.domain.services.weather import WeatherService
from src.domain.value_objects.weather import Weather


class CombatMechanicsService:
    _DEFAULT_STAB_MULTIPLIER: Final[float] = 1.0
    _DEFAULT_WEATHER_MULTIPLIER: Final[float] = 1.0

    @staticmethod
    def calculate_damage(
        *, attacker: Pokemon, defender: Pokemon, move: Move, weather: Weather = Weather.NO_WEATHER
    ) -> int:
        """Calculate the damage dealt by an attack.

        TODO: Add other modifiers.
        """
        stab_multiplier: float = (
            STAB_MULTIPLIER if move.type in attacker.types else CombatMechanicsService._DEFAULT_STAB_MULTIPLIER
        )
        # type_multiplier: float = TypeEffectivenessService.get_effectiveness_multiplier(
        #     attack_type=move.type, defender_type=defender.types
        # )
        type_multiplier = 1.0  # TODO finish
        weather_multiplier: float = (
            WEATHER_MULTIPLIER
            if WeatherService.is_type_boosted(weather=weather, type_=move.type)
            else CombatMechanicsService._DEFAULT_WEATHER_MULTIPLIER
        )
        result = floor(
            0.5
            * (attacker.attack / defender.defense)
            * stab_multiplier
            * move.power
            * type_multiplier
            * weather_multiplier
        )
        return result
