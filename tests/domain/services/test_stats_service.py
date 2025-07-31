from src.domain.services.stats_service import StatsService


class TestStatsService:
    """Test Stats Service."""

    def test_calculate_attack(self) -> None:
        """Test attack stat calculation."""
        assert StatsService.calculate_attack(base_attack=150, attack_iv=15, cpm=0.7317) == 120.7305
        assert StatsService.calculate_attack(base_attack=100, attack_iv=0, cpm=0.094) == 9.4

    def test_calculate_defense(self) -> None:
        """Test defense stat calculation."""
        assert StatsService.calculate_defense(base_defense=140, defense_iv=15, cpm=0.7317) == 113.4135
        assert StatsService.calculate_defense(base_defense=90, defense_iv=0, cpm=0.094) == 8.46

    def test_calculate_stamina(self) -> None:
        """Test stamina stat calculation."""
        assert StatsService.calculate_stamina(base_stamina=200, stamina_iv=15, cpm=0.7317) == 157
        assert StatsService.calculate_stamina(base_stamina=120, stamina_iv=0, cpm=0.094) == 11
