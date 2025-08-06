from src.domain.entities.max_boss import MaxBoss
from src.domain.entities.pokemon import Pokemon


class MaxMechanicsService:
    @staticmethod
    def get_cpm_by_damage(*, damage: int, target_pokemon: Pokemon, boss: MaxBoss) -> float:
        """Calculate the CPM of a move.

        TODO: Add other modifiers.
        """
        return 2.0  # TODO finish
