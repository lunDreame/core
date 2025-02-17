"""Test the Jewish calendar config flow."""

from unittest.mock import AsyncMock

import pytest

from homeassistant import config_entries, setup
from homeassistant.components.jewish_calendar import (
    CONF_CANDLE_LIGHT_MINUTES,
    CONF_DIASPORA,
    CONF_HAVDALAH_OFFSET_MINUTES,
    CONF_LANGUAGE,
    DEFAULT_CANDLE_LIGHT,
    DEFAULT_DIASPORA,
    DEFAULT_HAVDALAH_OFFSET_MINUTES,
    DEFAULT_LANGUAGE,
    DOMAIN,
)
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import (
    CONF_ELEVATION,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_NAME,
    CONF_TIME_ZONE,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component

from tests.common import MockConfigEntry


async def test_step_user(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test user config."""
    await setup.async_setup_component(hass, "persistent_notification", {})
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result2 = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_DIASPORA: DEFAULT_DIASPORA, CONF_LANGUAGE: DEFAULT_LANGUAGE},
    )

    assert result2["type"] is FlowResultType.CREATE_ENTRY

    await hass.async_block_till_done()
    assert len(mock_setup_entry.mock_calls) == 1

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].data[CONF_DIASPORA] == DEFAULT_DIASPORA
    assert entries[0].data[CONF_LANGUAGE] == DEFAULT_LANGUAGE
    assert entries[0].data[CONF_LATITUDE] == hass.config.latitude
    assert entries[0].data[CONF_LONGITUDE] == hass.config.longitude
    assert entries[0].data[CONF_ELEVATION] == hass.config.elevation
    assert entries[0].data[CONF_TIME_ZONE] == hass.config.time_zone


@pytest.mark.parametrize("diaspora", [True, False])
@pytest.mark.parametrize("language", ["hebrew", "english"])
async def test_import_no_options(hass: HomeAssistant, language, diaspora) -> None:
    """Test that the import step works."""
    conf = {
        DOMAIN: {CONF_NAME: "test", CONF_LANGUAGE: language, CONF_DIASPORA: diaspora}
    }

    assert await async_setup_component(hass, DOMAIN, conf.copy())
    await hass.async_block_till_done()

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].data == conf[DOMAIN] | {
        CONF_CANDLE_LIGHT_MINUTES: DEFAULT_CANDLE_LIGHT,
        CONF_HAVDALAH_OFFSET_MINUTES: DEFAULT_HAVDALAH_OFFSET_MINUTES,
    }


async def test_import_with_options(hass: HomeAssistant) -> None:
    """Test that the import step works."""
    conf = {
        DOMAIN: {
            CONF_NAME: "test",
            CONF_DIASPORA: DEFAULT_DIASPORA,
            CONF_LANGUAGE: DEFAULT_LANGUAGE,
            CONF_CANDLE_LIGHT_MINUTES: 20,
            CONF_HAVDALAH_OFFSET_MINUTES: 50,
            CONF_LATITUDE: 31.76,
            CONF_LONGITUDE: 35.235,
        }
    }

    assert await async_setup_component(hass, DOMAIN, conf.copy())
    await hass.async_block_till_done()

    entries = hass.config_entries.async_entries(DOMAIN)
    assert len(entries) == 1
    assert entries[0].data == conf[DOMAIN]


async def test_single_instance_allowed(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test we abort if already setup."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result.get("type") is FlowResultType.ABORT
    assert result.get("reason") == "single_instance_allowed"


async def test_options(hass: HomeAssistant, mock_config_entry: MockConfigEntry) -> None:
    """Test updating options."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(mock_config_entry.entry_id)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        user_input={
            CONF_CANDLE_LIGHT_MINUTES: 25,
            CONF_HAVDALAH_OFFSET_MINUTES: 34,
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_CANDLE_LIGHT_MINUTES] == 25
    assert result["data"][CONF_HAVDALAH_OFFSET_MINUTES] == 34
