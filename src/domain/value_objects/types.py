from enum import StrEnum


class Type(StrEnum):
    """Represents Pokémon types.

    Defines all valid Pokémon types with their canonical string representations.
    Each type corresponds to an elemental or conceptual category that affects
    battle mechanics and effectiveness calculations.
    """

    BUG = "Bug"
    DARK = "Dark"
    DRAGON = "Dragon"
    ELECTRIC = "Electric"
    FAIRY = "Fairy"
    FIGHTING = "Fighting"
    FIRE = "Fire"
    FLYING = "Flying"
    GHOST = "Ghost"
    GRASS = "Grass"
    GROUND = "Ground"
    ICE = "Ice"
    NORMAL = "Normal"
    POISON = "Poison"
    PSYCHIC = "Psychic"
    ROCK = "Rock"
    STEEL = "Steel"
    WATER = "Water"
