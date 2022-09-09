import pytest
from unittest import mock


@pytest.fixture(autouse=True)
def mock_slack_web_client():
    with mock.patch("slack_signals.signals.WebClient") as _fixture:
        yield _fixture
