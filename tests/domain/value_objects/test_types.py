import pytest

from src.domain.value_objects.types import Type


class TestType:
    """Test suite for Type value object."""

    def test_type_values_are_correct(self) -> None:
        """Test that Type enum has the correct string values."""
        assert Type.BUG == "Bug"
        assert Type.DARK == "Dark"
        assert Type.DRAGON == "Dragon"
        assert Type.ELECTRIC == "Electric"
        assert Type.FAIRY == "Fairy"
        assert Type.FIGHTING == "Fighting"
        assert Type.FIRE == "Fire"
        assert Type.FLYING == "Flying"
        assert Type.GHOST == "Ghost"
        assert Type.GRASS == "Grass"
        assert Type.GROUND == "Ground"
        assert Type.ICE == "Ice"
        assert Type.NORMAL == "Normal"
        assert Type.POISON == "Poison"
        assert Type.PSYCHIC == "Psychic"
        assert Type.ROCK == "Rock"
        assert Type.STEEL == "Steel"
        assert Type.WATER == "Water"

    def test_type_names_are_correct(self) -> None:
        """Test that Type enum names are properly capitalized."""
        assert Type.BUG.name == "BUG"
        assert Type.FIRE.name == "FIRE"
        assert Type.WATER.name == "WATER"
        assert Type.ELECTRIC.name == "ELECTRIC"

    def test_type_count(self) -> None:
        """Test that we have exactly 18 types defined."""
        assert len(Type) == 18

    def test_all_pokemon_types_included(self) -> None:
        """Test that all traditional Pokemon types are included."""
        expected_types = {
            "Bug",
            "Dark",
            "Dragon",
            "Electric",
            "Fairy",
            "Fighting",
            "Fire",
            "Flying",
            "Ghost",
            "Grass",
            "Ground",
            "Ice",
            "Normal",
            "Poison",
            "Psychic",
            "Rock",
            "Steel",
            "Water",
        }
        actual_types = {t.value for t in Type}
        assert actual_types == expected_types

    def test_type_string_equality(self) -> None:
        """Test that Type values can be compared with strings."""
        assert Type.FIRE == "Fire"
        assert Type.WATER == "Water"
        assert Type.ELECTRIC != "electric"  # Case sensitive

    def test_type_membership(self) -> None:
        """Test that string values are correctly identified as Type members."""
        assert "Fire" in Type
        assert "Water" in Type
        assert "fire" not in Type  # Case sensitive
        assert "Unknown" not in Type

    def test_type_from_value(self) -> None:
        """Test creating Type instances from their string values."""
        assert Type("Fire") == Type.FIRE
        assert Type("Water") == Type.WATER
        assert Type("Electric") == Type.ELECTRIC

    def test_invalid_type_value_raises_error(self) -> None:
        """Test that invalid type values raise ValueError."""
        with pytest.raises(ValueError):
            Type("Unknown")

        with pytest.raises(ValueError):
            Type("fire")  # Case sensitive

        with pytest.raises(ValueError):
            Type("")

    def test_type_is_immutable(self) -> None:
        """Test that Type values cannot be modified."""
        type_fire = Type.FIRE
        with pytest.raises(AttributeError):
            type_fire.value = "Flame"  # type: ignore

    def test_type_string_representation(self) -> None:
        """Test string representation of Type values."""
        assert str(Type.FIRE) == "Fire"
        assert repr(Type.FIRE) == "<Type.FIRE: 'Fire'>"

    def test_type_ordering(self) -> None:
        """Test that types can be sorted alphabetically by their values."""
        types = [Type.WATER, Type.FIRE, Type.ELECTRIC, Type.BUG]
        sorted_types = sorted(types, key=lambda t: t.value)
        expected_order = [Type.BUG, Type.ELECTRIC, Type.FIRE, Type.WATER]
        assert sorted_types == expected_order

    def test_type_case_sensitivity(self) -> None:
        """Test that Type enum is case sensitive for values."""
        assert Type.FIRE.value == "Fire"
        assert Type.FIRE.value != "fire"
        assert Type.FIRE.value != "FIRE"
