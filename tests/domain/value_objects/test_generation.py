import pytest

from src.domain.value_objects.generation import Generation


class TestGeneration:
    """Test suite for Generation value object."""

    def test_generation_values_are_correct(self) -> None:
        """Test that Generation enum has the correct values for each generation."""
        assert Generation.KANTO == 1
        assert Generation.JOHTO == 2
        assert Generation.HOENN == 3
        assert Generation.SINNOH == 4
        assert Generation.UNOVA == 5
        assert Generation.KALOS == 6
        assert Generation.ALOLA == 7
        assert Generation.GALAR == 8
        assert Generation.PALDEA == 9

    def test_generation_names_are_correct(self) -> None:
        """Test that Generation enum names match expected region names."""
        assert Generation.KANTO.name == "KANTO"
        assert Generation.JOHTO.name == "JOHTO"
        assert Generation.HOENN.name == "HOENN"
        assert Generation.SINNOH.name == "SINNOH"
        assert Generation.UNOVA.name == "UNOVA"
        assert Generation.KALOS.name == "KALOS"
        assert Generation.ALOLA.name == "ALOLA"
        assert Generation.GALAR.name == "GALAR"
        assert Generation.PALDEA.name == "PALDEA"

    def test_generation_count(self) -> None:
        """Test that we have exactly 9 generations defined."""
        assert len(Generation) == 9

    def test_generation_comparison(self) -> None:
        """Test that generations can be compared using their numeric values."""
        assert Generation.KANTO < Generation.JOHTO
        assert Generation.PALDEA > Generation.KANTO
        assert Generation.HOENN == Generation.HOENN

    def test_generation_ordering(self) -> None:
        """Test that generations are properly ordered chronologically."""
        generations = list(Generation)
        sorted_generations = sorted(generations)
        assert generations == sorted_generations

    def test_generation_membership(self) -> None:
        """Test that values are correctly identified as Generation members."""
        assert 1 in Generation
        assert 9 in Generation
        assert 0 not in Generation
        assert 10 not in Generation

    def test_generation_from_value(self) -> None:
        """Test creating Generation instances from their numeric values."""
        assert Generation(1) == Generation.KANTO
        assert Generation(9) == Generation.PALDEA

    def test_invalid_generation_value_raises_error(self) -> None:
        """Test that invalid generation values raise ValueError."""
        with pytest.raises(ValueError):
            Generation(0)

        with pytest.raises(ValueError):
            Generation(10)

        with pytest.raises(ValueError):
            Generation(-1)

    def test_generation_is_immutable(self) -> None:
        """Test that Generation values cannot be modified."""
        gen = Generation.KANTO
        with pytest.raises(AttributeError):
            gen.value = 5  # type: ignore
