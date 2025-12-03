"""The Sporet integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import CONF_BEARER_TOKEN, CONF_SLOPE_ID, DOMAIN
from .coordinator import SporetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sporet from a config entry."""
    slope_id = entry.data.get(CONF_SLOPE_ID)
    bearer_token = entry.data.get(CONF_BEARER_TOKEN)

    if not slope_id:
        _LOGGER.error("Slope ID not found in config entry")
        return False

    if not bearer_token:
        _LOGGER.error("Bearer token not found in config entry")
        return False

    coordinator = SporetDataUpdateCoordinator(
        hass, bearer_token, slope_id
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_update_options))

    return True


async def async_update_options(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

