import pytest

from src.domain.value_objects.tier import Tier


class TestTier:
    """Test suite for the Tier value object."""

    def test_tier_values(self) -> None:
        """Test that all tier values are correctly defined."""
        assert Tier.TIER_1 == "T1"
        assert Tier.TIER_2 == "T2"
        assert Tier.TIER_3 == "T3"
        assert Tier.TIER_4 == "T4"
        assert Tier.TIER_5 == "T5"
        assert Tier.TIER_6 == "T6"

    def test_tier_ordering(self) -> None:
        """Test that tiers can be properly ordered."""
        assert Tier.TIER_1 < Tier.TIER_2
        assert Tier.TIER_2 < Tier.TIER_6
        assert Tier.TIER_6 > Tier.TIER_1
        assert Tier.TIER_3 <= Tier.TIER_3
        assert Tier.TIER_4 >= Tier.TIER_4

    def test_tier_str_conversion(self) -> None:
        """Test that tiers can be converted to strings."""
        assert str(Tier.TIER_1) == "T1"
        assert str(Tier.TIER_6) == "T6"

    def test_tier_from_str(self) -> None:
        """Test that tiers can be created from string values."""
        assert Tier("T1") == Tier.TIER_1
        assert Tier("T6") == Tier.TIER_6

    def test_tier_invalid_value(self) -> None:
        """Test that invalid tier values raise appropriate errors."""
        with pytest.raises(ValueError):
            Tier("T0")
        with pytest.raises(ValueError):
            Tier("T7")
        with pytest.raises(ValueError):
            Tier("invalid")

    def test_tier_count(self) -> None:
        """Test that there are exactly 6 tiers defined."""
        assert len(Tier) == 6

    def test_tier_membership(self) -> None:
        """Test tier membership operations."""
        assert "T1" in Tier
        assert "T6" in Tier
        assert "T0" not in Tier
        assert "T7" not in Tier
