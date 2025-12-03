"""API client for Sporet."""

import logging
from typing import Any
import aiohttp

from .const import API_BASE_URL

_LOGGER = logging.getLogger(__name__)


class SporetAPIError(Exception):
    """Exception raised for API errors."""


class SporetAPI:
    """API client for Sporet."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        bearer_token: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._bearer_token = bearer_token

    async def async_get_route_details(self, slope_id: str) -> dict[str, Any]:
        """Get route details from the API."""
        url = f"{API_BASE_URL}/{slope_id}/details"

        try:
            headers = {
                "Authorization": f"Bearer {self._bearer_token}",
                "Content-Type": "application/json",
            }

            async with self._session.get(url, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()
                _LOGGER.debug("API response for route %s: %s", slope_id, data)
                return data

        except aiohttp.ClientError as err:
            _LOGGER.error("Error fetching route details: %s", err)
            raise SporetAPIError(f"Error fetching route details: {err}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error: %s", err)
            raise SporetAPIError(f"Unexpected error: {err}") from err
