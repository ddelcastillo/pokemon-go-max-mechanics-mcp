from src.domain.constants.weather_boost import WEATHER_TYPE_BOOSTS
from src.domain.value_objects.types import Type
from src.domain.value_objects.weather import Weather


class WeatherService:
    """Domain service for weather boost calculations.

    Encapsulates business logic for determining which Pokemon types
    receive damage boosts under specific weather conditions.
    """

    @staticmethod
    def get_boosted_types(*, weather: Weather) -> frozenset[Type]:
        """Get all Pokemon types that are boosted by the given weather.

        Args:
            weather: The weather condition to check for boosts

        Returns:
            A frozenset of Types that receive damage boosts under the given weather.
            Returns empty frozenset for NO_WEATHER.

        Examples:
            weather=Weather.SUNNY -> {Type.FIRE, Type.GRASS, Type.GROUND}
            weather=Weather.NO_WEATHER -> frozenset()
        """
        return WEATHER_TYPE_BOOSTS[weather]

    @staticmethod
    def is_type_boosted(*, weather: Weather, type_: Type) -> bool:
        """Check if a specific Pokemon type is boosted by the given weather.

        Args:
            weather: The weather condition to check.
            type_: The type to check for boost.

        Returns:
            True if the type receives a damage boost under the given weather,
            False otherwise.

        Examples:
            weather=Weather.SUNNY, type_=Type.FIRE -> True
            weather=Weather.SUNNY, type_=Type.WATER -> False
            weather=Weather.NO_WEATHER, type_=Type.FIRE -> False
        """
        return type_ in WEATHER_TYPE_BOOSTS[weather]
