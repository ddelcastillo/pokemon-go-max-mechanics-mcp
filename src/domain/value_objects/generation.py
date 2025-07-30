from enum import IntEnum


class Generation(IntEnum):
    """Represents the generation of Pokémon games.

    Each generation corresponds to a major release of Pokémon games,
    numbered sequentially from 1 (Kanto) to 9 (Paldea).
    """

    KANTO = 1
    JOHTO = 2
    HOENN = 3
    SINNOH = 4
    UNOVA = 5
    KALOS = 6
    ALOLA = 7
    GALAR = 8
    PALDEA = 9
