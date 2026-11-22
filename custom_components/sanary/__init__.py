"""Sanary-sur-Mer integration: for now, free parking spaces."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .coordinator import SanaryUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

SanaryConfigEntry = ConfigEntry[SanaryUpdateCoordinator]


async def async_setup_entry(
    hass: HomeAssistant, entry: SanaryConfigEntry
) -> bool:
    """Set up the integration from a config entry."""
    coordinator = SanaryUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SanaryConfigEntry
) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def _async_update_listener(
    hass: HomeAssistant, entry: SanaryConfigEntry
) -> None:
    """Reload the config entry when its options change."""
    await hass.config_entries.async_reload(entry.entry_id)
