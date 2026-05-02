import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from services import ai_explainer


@pytest.mark.asyncio
async def test_generates_explanation():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Your CPU is overheating. Clean the vents.")]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    ai_explainer._cache.clear()
    ai_explainer._client = mock_client

    machine = {"machine_id": "test-123", "hostname": "MyPC", "os_name": "macOS", "cpu_model": "M2"}
    scan = {"health_score": 55, "score_performance": 65, "score_storage": 80, "score_security": 90, "score_stability": 85}
    issues = [{"issue_code": "P01", "severity": "high", "title": "Thermal throttling", "description": "CPU too hot"}]

    explanation, cached = await ai_explainer.generate_explanation(machine, scan, issues)

    assert "CPU" in explanation
    assert cached is False
    mock_client.messages.create.assert_called_once()


@pytest.mark.asyncio
async def test_returns_cached_on_second_call():
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Cached explanation")]

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_response)

    ai_explainer._cache.clear()
    ai_explainer._client = mock_client

    machine = {"machine_id": "cache-test", "hostname": "PC", "os_name": "Linux", "cpu_model": "i7"}
    scan = {"health_score": 45, "score_performance": 50, "score_storage": 60, "score_security": 70, "score_stability": 80}
    issues = []

    _, cached1 = await ai_explainer.generate_explanation(machine, scan, issues)
    _, cached2 = await ai_explainer.generate_explanation(machine, scan, issues)

    assert cached1 is False
    assert cached2 is True
    assert mock_client.messages.create.call_count == 1


@pytest.mark.asyncio
async def test_prompt_includes_machine_info():
    machine = {"machine_id": "m1", "hostname": "WorkPC", "os_name": "Windows", "cpu_model": "Ryzen 9"}
    scan = {"health_score": 40, "score_performance": 30, "score_storage": 70, "score_security": 80, "score_stability": 75}
    issues = [{"issue_code": "P03", "severity": "high", "title": "Memory leak", "description": "Process using too much RAM"}]

    prompt = ai_explainer._build_prompt(machine, scan, issues)

    assert "WorkPC" in prompt
    assert "Windows" in prompt
    assert "Ryzen 9" in prompt
    assert "P03" in prompt
    assert "Memory leak" in prompt
