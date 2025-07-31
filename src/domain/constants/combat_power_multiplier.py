from math import sqrt
from typing import Final

_BASE_LEVEL_CPMS: Final[list[float]] = [  # From Game Master.
    0.094,
    0.16639787,
    0.21573247,
    0.25572005,
    0.29024988,
    0.3210876,
    0.34921268,
    0.3752356,
    0.39956728,
    0.4225,
    0.44310755,
    0.4627984,
    0.48168495,
    0.49985844,
    0.51739395,
    0.5343543,
    0.5507927,
    0.5667545,
    0.5822789,
    0.5974,
    0.6121573,
    0.6265671,
    0.64065295,
    0.65443563,
    0.667934,
    0.6811649,
    0.69414365,
    0.7068842,
    0.7193991,
    0.7317,
    0.7377695,
    0.74378943,
    0.74976104,
    0.7556855,
    0.76156384,
    0.76739717,
    0.7731865,
    0.77893275,
    0.784637,
    0.7903,
    0.7953,
    0.8003,
    0.8053,
    0.8103,
    0.8153,
    0.8203,
    0.8253,
    0.8303,
    0.8353,
    0.8403,
    0.8453,
    0.8503,
    0.8553,
    0.8603,
    0.8653,
]


def _cpm_interpolation_formula(*, previous_cpm: float, next_cpm: float) -> float:
    """Calculate the CPM for half levels using interpolation formula.

    Args:
        previous_cpm: The CPM value for the previous whole level
        next_cpm: The CPM value for the next whole level

    Returns:
        The interpolated CPM value for the half level
    """
    return sqrt((previous_cpm**2 + next_cpm**2) / 2)


def _generate_combat_power_multiplier() -> dict[float, float]:
    """Generate the complete combat power multiplier mapping.

    Returns:
        A dictionary mapping levels to their CPM values.
    """
    cpm_mapping: dict[float, float] = {}

    for level_index, cpm in enumerate(_BASE_LEVEL_CPMS[:-1], start=1):
        cpm_mapping[float(level_index)] = cpm
        cpm_mapping[float(level_index) + 0.5] = _cpm_interpolation_formula(
            previous_cpm=cpm, next_cpm=_BASE_LEVEL_CPMS[level_index]
        )
    cpm_mapping[float(len(_BASE_LEVEL_CPMS))] = _BASE_LEVEL_CPMS[-1]

    return cpm_mapping


COMBAT_POWER_MULTIPLIER: Final[dict[float, float]] = _generate_combat_power_multiplier()
MIN_CPM: Final[float] = COMBAT_POWER_MULTIPLIER[1.0]
MAX_CPM: Final[float] = COMBAT_POWER_MULTIPLIER[float(len(_BASE_LEVEL_CPMS))]
