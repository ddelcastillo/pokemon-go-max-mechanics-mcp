from src.domain.services.weather_service import WeatherService
from src.domain.value_objects.types import Type
from src.domain.value_objects.weather import Weather


class TestWeatherService:
    """Test suite for WeatherService."""

    def test_get_boosted_types_sunny_weather(self) -> None:
        """Test getting boosted types for sunny weather."""
        result = WeatherService.get_boosted_types(weather=Weather.SUNNY)
        expected = {Type.FIRE, Type.GRASS, Type.GROUND}
        assert result == expected

    def test_get_boosted_types_partly_cloudy_weather(self) -> None:
        """Test getting boosted types for partly cloudy weather."""
        result = WeatherService.get_boosted_types(weather=Weather.PARTLY_CLOUDY)
        expected = {Type.NORMAL, Type.ROCK}
        assert result == expected

    def test_get_boosted_types_cloudy_weather(self) -> None:
        """Test getting boosted types for cloudy weather."""
        result = WeatherService.get_boosted_types(weather=Weather.CLOUDY)
        expected = {Type.FAIRY, Type.FIGHTING, Type.POISON}
        assert result == expected

    def test_get_boosted_types_rainy_weather(self) -> None:
        """Test getting boosted types for rainy weather."""
        result = WeatherService.get_boosted_types(weather=Weather.RAINY)
        expected = {Type.ELECTRIC, Type.WATER, Type.BUG}
        assert result == expected

    def test_get_boosted_types_snow_weather(self) -> None:
        """Test getting boosted types for snow weather."""
        result = WeatherService.get_boosted_types(weather=Weather.SNOW)
        expected = {Type.ICE, Type.STEEL}
        assert result == expected

    def test_get_boosted_types_windy_weather(self) -> None:
        """Test getting boosted types for windy weather."""
        result = WeatherService.get_boosted_types(weather=Weather.WINDY)
        expected = {Type.DRAGON, Type.FLYING, Type.PSYCHIC}
        assert result == expected

    def test_get_boosted_types_fog_weather(self) -> None:
        """Test getting boosted types for fog weather."""
        result = WeatherService.get_boosted_types(weather=Weather.FOG)
        expected = {Type.DARK, Type.GHOST}
        assert result == expected

    def test_get_boosted_types_no_weather(self) -> None:
        """Test getting boosted types for no weather returns empty set."""
        result = WeatherService.get_boosted_types(weather=Weather.NO_WEATHER)
        expected: frozenset[Type] = frozenset()
        assert result == expected

    def test_get_boosted_types_returns_frozenset(self) -> None:
        """Test that get_boosted_types returns a frozenset."""
        result = WeatherService.get_boosted_types(weather=Weather.SUNNY)
        assert isinstance(result, frozenset)

    def test_is_type_boosted_fire_in_sunny(self) -> None:
        """Test that Fire type is boosted in sunny weather."""
        result = WeatherService.is_type_boosted(weather=Weather.SUNNY, pokemon_type=Type.FIRE)
        assert result is True

    def test_is_type_boosted_water_in_sunny(self) -> None:
        """Test that Water type is not boosted in sunny weather."""
        result = WeatherService.is_type_boosted(weather=Weather.SUNNY, pokemon_type=Type.WATER)
        assert result is False

    def test_is_type_boosted_water_in_rainy(self) -> None:
        """Test that Water type is boosted in rainy weather."""
        result = WeatherService.is_type_boosted(weather=Weather.RAINY, pokemon_type=Type.WATER)
        assert result is True

    def test_is_type_boosted_fire_in_rainy(self) -> None:
        """Test that Fire type is not boosted in rainy weather."""
        result = WeatherService.is_type_boosted(weather=Weather.RAINY, pokemon_type=Type.FIRE)
        assert result is False

    def test_is_type_boosted_all_types_in_no_weather(self) -> None:
        """Test that no type is boosted in no weather."""
        for pokemon_type in Type:
            result = WeatherService.is_type_boosted(weather=Weather.NO_WEATHER, pokemon_type=pokemon_type)
            assert result is False

    def test_is_type_boosted_returns_boolean(self) -> None:
        """Test that is_type_boosted returns a boolean."""
        result = WeatherService.is_type_boosted(weather=Weather.SUNNY, pokemon_type=Type.FIRE)
        assert isinstance(result, bool)

    def test_static_methods_can_be_called_without_instance(self) -> None:
        """Test that service methods can be called statically."""
        boosted_types = WeatherService.get_boosted_types(weather=Weather.SUNNY)
        is_boosted = WeatherService.is_type_boosted(weather=Weather.SUNNY, pokemon_type=Type.FIRE)

        assert len(boosted_types) == 3
        assert is_boosted is True

    def test_consistency_between_methods(self) -> None:
        """Test that both methods are consistent with each other."""
        assert all(
            WeatherService.is_type_boosted(weather=weather, pokemon_type=pokemon_type)
            == (pokemon_type in WeatherService.get_boosted_types(weather=weather))
            for weather in Weather
            for pokemon_type in Type
        ), "Methods should be consistent for all weather and type combinations"
