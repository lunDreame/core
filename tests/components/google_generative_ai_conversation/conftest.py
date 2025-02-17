"""Tests helpers."""

from unittest.mock import patch

import pytest

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_LLM_HASS_API
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry


@pytest.fixture
def mock_genai():
    """Mock the genai call in async_setup_entry."""
    with patch(
        "homeassistant.components.google_generative_ai_conversation.genai.list_models",
        return_value=iter([]),
    ):
        yield


@pytest.fixture
def mock_config_entry(hass, mock_genai):
    """Mock a config entry."""
    entry = MockConfigEntry(
        domain="google_generative_ai_conversation",
        title="Google Generative AI Conversation",
        data={
            "api_key": "bla",
        },
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_config_entry_with_assist(hass, mock_config_entry):
    """Mock a config entry with assist."""
    hass.config_entries.async_update_entry(
        mock_config_entry, options={CONF_LLM_HASS_API: llm.LLM_API_ASSIST}
    )
    return mock_config_entry


@pytest.fixture
async def mock_init_component(hass: HomeAssistant, mock_config_entry: ConfigEntry):
    """Initialize integration."""
    with patch("google.generativeai.get_model"):
        assert await async_setup_component(
            hass, "google_generative_ai_conversation", {}
        )
        await hass.async_block_till_done()


@pytest.fixture(autouse=True)
async def setup_ha(hass: HomeAssistant) -> None:
    """Set up Home Assistant."""
    assert await async_setup_component(hass, "homeassistant", {})
