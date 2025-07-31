from enum import StrEnum


class Tier(StrEnum):
    """Represents Max Boss tier levels in Pokemon Go.

    Each tier corresponds to the difficulty and reward level of Max Boss battles,
    ranging from Tier 1 (easiest) to Tier 6 (Gigantamax).
    Higher tiers typically require more players and offer better rewards.
    """

    TIER_1 = "T1"
    TIER_2 = "T2"
    TIER_3 = "T3"
    TIER_4 = "T4"
    TIER_5 = "T5"
    TIER_6 = "T6"  # Gigantamax
