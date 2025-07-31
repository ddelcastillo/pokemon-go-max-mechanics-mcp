import pytest

from src.domain.value_objects.weather import Weather


class TestWeather:
    """Test suite for Weather value object."""

    def test_weather_values_are_correct(self) -> None:
        """Test that Weather enum has the correct string values."""
        assert Weather.SUNNY == "Sunny"
        assert Weather.PARTLY_CLOUDY == "Partly Cloudy"
        assert Weather.CLOUDY == "Cloudy"
        assert Weather.RAINY == "Rainy"
        assert Weather.SNOW == "Snow"
        assert Weather.WINDY == "Windy"
        assert Weather.FOG == "Fog"
        assert Weather.NO_WEATHER == "No Weather"

    def test_weather_names_are_correct(self) -> None:
        """Test that Weather enum names are properly capitalized."""
        assert Weather.SUNNY.name == "SUNNY"
        assert Weather.PARTLY_CLOUDY.name == "PARTLY_CLOUDY"
        assert Weather.CLOUDY.name == "CLOUDY"
        assert Weather.NO_WEATHER.name == "NO_WEATHER"

    def test_weather_count(self) -> None:
        """Test that we have exactly 8 weather conditions defined."""
        assert len(Weather) == 8

    def test_all_pokemon_go_weathers_included(self) -> None:
        """Test that all Pokemon Go weather conditions are included."""
        expected_weathers = {
            "Sunny",
            "Partly Cloudy",
            "Cloudy",
            "Rainy",
            "Snow",
            "Windy",
            "Fog",
            "No Weather",
        }
        actual_weathers = {w.value for w in Weather}
        assert actual_weathers == expected_weathers

    def test_weather_string_equality(self) -> None:
        """Test that Weather values can be compared with strings."""
        assert Weather.SUNNY == "Sunny"
        assert Weather.RAINY == "Rainy"
        assert Weather.SUNNY != "sunny"  # Case sensitive

    def test_weather_membership(self) -> None:
        """Test that string values are correctly identified as Weather members."""
        assert "Sunny" in Weather
        assert "Rainy" in Weather
        assert "sunny" not in Weather  # Case sensitive
        assert "Unknown" not in Weather

    def test_weather_from_value(self) -> None:
        """Test creating Weather instances from their string values."""
        assert Weather("Sunny") == Weather.SUNNY
        assert Weather("Rainy") == Weather.RAINY
        assert Weather("No Weather") == Weather.NO_WEATHER

    def test_invalid_weather_value_raises_error(self) -> None:
        """Test that invalid weather values raise ValueError."""
        with pytest.raises(ValueError):
            Weather("Unknown")

        with pytest.raises(ValueError):
            Weather("sunny")  # Case sensitive

        with pytest.raises(ValueError):
            Weather("")

    def test_weather_is_immutable(self) -> None:
        """Test that Weather values cannot be modified."""
        weather_sunny = Weather.SUNNY
        with pytest.raises(AttributeError):
            weather_sunny.value = "Bright"  # type: ignore

    def test_weather_string_representation(self) -> None:
        """Test string representation of Weather values."""
        assert str(Weather.SUNNY) == "Sunny"
        assert repr(Weather.SUNNY) == "<Weather.SUNNY: 'Sunny'>"

    def test_weather_ordering(self) -> None:
        """Test that weathers can be sorted alphabetically by their values."""
        weathers = [Weather.WINDY, Weather.CLOUDY, Weather.SUNNY]
        sorted_weathers = sorted(weathers, key=lambda w: w.value)
        expected_order = [Weather.CLOUDY, Weather.SUNNY, Weather.WINDY]
        assert sorted_weathers == expected_order

    def test_weather_case_sensitivity(self) -> None:
        """Test that Weather enum is case sensitive for values."""
        assert Weather.SUNNY.value == "Sunny"
        assert Weather.SUNNY.value != "sunny"
        assert Weather.SUNNY.value != "SUNNY"

    def test_no_weather_option_exists(self) -> None:
        """Test that NO_WEATHER option exists for calculations without weather."""
        assert Weather.NO_WEATHER in Weather
        assert Weather.NO_WEATHER == "No Weather"
