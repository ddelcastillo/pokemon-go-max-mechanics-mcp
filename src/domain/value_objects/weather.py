from enum import StrEnum


class Weather(StrEnum):
    """Represents Pokemon Go weather conditions.

    Defines all valid weather conditions that can affect Pokemon spawns
    and battle mechanics through type effectiveness boosts.
    Includes NO_WEATHER for calculations without weather effects.
    """

    SUNNY = "Sunny"
    PARTLY_CLOUDY = "Partly Cloudy"
    CLOUDY = "Cloudy"
    RAINY = "Rainy"
    SNOW = "Snow"
    WINDY = "Windy"
    FOG = "Fog"
    NO_WEATHER = "No Weather"
