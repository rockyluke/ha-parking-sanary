"""Data update coordinator for the Sanary-sur-Mer integration."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import timedelta
from typing import Any

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN, ENDPOINT, STALE_FACTOR

_LOGGER = logging.getLogger(__name__)


class SanaryUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Fetch and shape the parking data of Sanary-sur-Mer."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        interval = int(
            entry.options.get("scan_interval")
            or entry.data.get("scan_interval")
            or DEFAULT_SCAN_INTERVAL
        )
        self.stale_after = max(90, interval * STALE_FACTOR)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=interval),
        )

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Query the city hall endpoint and shape the response."""
        session = async_get_clientsession(self.hass)
        try:
            async with asyncio.timeout(15):
                response = await session.get(
                    ENDPOINT,
                    params={"v": str(int(time.time()))},
                )
                response.raise_for_status()
                payload = await response.json()
        except (TimeoutError, aiohttp.ClientError) as err:
            raise UpdateFailed(f"Unable to reach the city hall data: {err}") from err
        except ValueError as err:
            raise UpdateFailed(f"Invalid response format: {err}") from err

        counters = payload.get("mapCounters")
        if not isinstance(counters, dict):
            raise UpdateFailed("Unexpected format: 'mapCounters' missing.")

        timestamp = payload.get("timestamp") or 0
        age = time.time() - float(timestamp) / 1000 if timestamp else None

        data: dict[str, dict[str, Any]] = {}
        for counter_id, counter in counters.items():
            if not isinstance(counter, dict):
                continue
            status = str(counter.get("status", "unknown"))
            free = counter.get("freeSpaces")
            fresh = age is not None and age <= self.stale_after
            data[str(counter_id)] = {
                "free": int(free)
                if isinstance(free, (int, float)) and status != "off" and fresh
                else None,
                "status": status,
                "message": counter.get("message") or None,
                "age": age,
            }
        return data
