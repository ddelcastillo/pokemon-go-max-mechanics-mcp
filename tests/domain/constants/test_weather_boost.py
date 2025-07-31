from src.domain.constants.weather_boost import (
    WEATHER_BOOST_MULTIPLIER,
    WEATHER_TYPE_BOOSTS,
)
from src.domain.value_objects.types import Type
from src.domain.value_objects.weather import Weather


class TestWeatherBoost:
    """Test weather boost constants."""

    def test_weather_boost_multiplier_value(self) -> None:
        """Test that the weather boost multiplier is correct for Pokemon Go."""
        assert WEATHER_BOOST_MULTIPLIER == 1.2

    def test_sunny_weather_boosts(self) -> None:
        """Test that sunny weather boosts Fire, Grass, and Ground types."""
        expected_types = {Type.FIRE, Type.GRASS, Type.GROUND}
        assert WEATHER_TYPE_BOOSTS[Weather.SUNNY] == expected_types

    def test_partly_cloudy_weather_boosts(self) -> None:
        """Test that partly cloudy weather boosts Normal and Rock types."""
        expected_types = {Type.NORMAL, Type.ROCK}
        assert WEATHER_TYPE_BOOSTS[Weather.PARTLY_CLOUDY] == expected_types

    def test_cloudy_weather_boosts(self) -> None:
        """Test that cloudy weather boosts Fairy, Fighting, and Poison types."""
        expected_types = {Type.FAIRY, Type.FIGHTING, Type.POISON}
        assert WEATHER_TYPE_BOOSTS[Weather.CLOUDY] == expected_types

    def test_rainy_weather_boosts(self) -> None:
        """Test that rainy weather boosts Electric, Water, and Bug types."""
        expected_types = {Type.ELECTRIC, Type.WATER, Type.BUG}
        assert WEATHER_TYPE_BOOSTS[Weather.RAINY] == expected_types

    def test_snow_weather_boosts(self) -> None:
        """Test that snow weather boosts Ice and Steel types."""
        expected_types = {Type.ICE, Type.STEEL}
        assert WEATHER_TYPE_BOOSTS[Weather.SNOW] == expected_types

    def test_windy_weather_boosts(self) -> None:
        """Test that windy weather boosts Dragon, Flying, and Psychic types."""
        expected_types = {Type.DRAGON, Type.FLYING, Type.PSYCHIC}
        assert WEATHER_TYPE_BOOSTS[Weather.WINDY] == expected_types

    def test_fog_weather_boosts(self) -> None:
        """Test that fog weather boosts Dark and Ghost types."""
        expected_types = {Type.DARK, Type.GHOST}
        assert WEATHER_TYPE_BOOSTS[Weather.FOG] == expected_types

    def test_no_weather_boosts_nothing(self) -> None:
        """Test that no weather boosts no types."""
        expected_types: frozenset[Type] = frozenset()
        assert WEATHER_TYPE_BOOSTS[Weather.NO_WEATHER] == expected_types

    def test_all_weather_conditions_mapped(self) -> None:
        """Test that all weather conditions have mappings."""
        assert len(WEATHER_TYPE_BOOSTS) == len(Weather)
        assert all(weather in WEATHER_TYPE_BOOSTS for weather in Weather)

    def test_total_boosted_types_count(self) -> None:
        """Test that exactly 18 types are boosted across all weathers (all types except None for NO_WEATHER)."""
        all_boosted_types: set[Type] = {
            type_ for weather, types in WEATHER_TYPE_BOOSTS.items() if weather != Weather.NO_WEATHER for type_ in types
        }

        assert len(all_boosted_types) == len(Type)
        assert all_boosted_types == set(Type)
