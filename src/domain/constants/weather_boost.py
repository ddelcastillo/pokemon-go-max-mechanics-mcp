from typing import Final

from src.domain.value_objects.types import Type
from src.domain.value_objects.weather import Weather

WEATHER_BOOST_MULTIPLIER: Final[float] = 1.2

WEATHER_TYPE_BOOSTS: Final[dict[Weather, frozenset[Type]]] = {
    Weather.SUNNY: frozenset({Type.FIRE, Type.GRASS, Type.GROUND}),
    Weather.PARTLY_CLOUDY: frozenset({Type.NORMAL, Type.ROCK}),
    Weather.CLOUDY: frozenset({Type.FAIRY, Type.FIGHTING, Type.POISON}),
    Weather.RAINY: frozenset({Type.ELECTRIC, Type.WATER, Type.BUG}),
    Weather.SNOW: frozenset({Type.ICE, Type.STEEL}),
    Weather.WINDY: frozenset({Type.DRAGON, Type.FLYING, Type.PSYCHIC}),
    Weather.FOG: frozenset({Type.DARK, Type.GHOST}),
    Weather.NO_WEATHER: frozenset(),
}
