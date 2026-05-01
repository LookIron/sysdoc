import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.schemas import Issue
from services.scorer import calculate


def _issue(code: str) -> Issue:
    return Issue(code=code, severity="high", title=code, description="")


class TestScorer:
    def test_clean_system_scores_100(self):
        result = calculate([])
        assert result.health_score == 100
        assert result.score_performance == 100
        assert result.score_storage == 100

    def test_p01_deducts_performance(self):
        result = calculate([_issue("P01")])
        assert result.score_performance == 80
        assert result.score_storage == 100

    def test_p02_deducts_storage(self):
        result = calculate([_issue("P02")])
        assert result.score_storage == 75
        assert result.score_performance == 100

    def test_multiple_issues_stack(self):
        result = calculate([_issue("P01"), _issue("P03"), _issue("P02")])
        assert result.score_performance == 65  # 100 - 20 - 15
        assert result.score_storage == 75      # 100 - 25

    def test_scores_clamped_at_zero(self):
        issues = [_issue("P01"), _issue("P03"), _issue("P07"), _issue("P08"), _issue("P09")]
        result = calculate(issues)
        assert result.score_performance >= 0

    def test_health_score_weighted_average(self):
        result = calculate([_issue("P01")])
        # performance=80, storage=100, security=100, stability=100
        expected = round(80 * 0.40 + 100 * 0.30 + 100 * 0.15 + 100 * 0.15)
        assert result.health_score == expected

    def test_health_score_clamped_to_100(self):
        result = calculate([])
        assert result.health_score <= 100

    def test_p09_deducts_both_performance_and_security(self):
        result = calculate([_issue("P09")])
        assert result.score_performance == 95
        assert result.score_security == 90
