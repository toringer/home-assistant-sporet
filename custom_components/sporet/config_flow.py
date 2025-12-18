"""Config flow for Sporet integration."""

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    API_BASE_URL,
    API_SEGMENT_URL,
    CONF_BEARER_TOKEN,
    CONF_IS_SEGMENT,
    CONF_SLOPE_ID,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


def sanitize_bearer_token(bearer_token: str) -> str:
    """Handle various permutations of the bearer token."""
    bearer_token = " ".join(bearer_token.strip().split())
    if bearer_token.lower().startswith("authorization"):
        bearer_token = bearer_token.split(" ")[2].strip()
    if bearer_token.lower().startswith("bearer"):
        bearer_token = bearer_token.split(" ")[1].strip()
    return bearer_token


def sanitize_slope_id(slope_id: str) -> str:
    """Allow user to paste the full URL to the slope."""
    # Slope  : https://sporet.no/share/Slope/10490?name=Bergsj%C3%B8-Randan-Nysetlia
    # Segment: https://sporet.no/share/SlopeSegment/131219?name=Segment
    if slope_id.lower().startswith("https:"):
        slope_id = slope_id.split("/")[5].split("?")[0].strip()
    return slope_id


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    bearer_token = data[CONF_BEARER_TOKEN]
    slope_id = data[CONF_SLOPE_ID]

    session = async_get_clientsession(hass)
    slope_url = f"{API_BASE_URL}/{slope_id}/details"
    segment_url = f"{API_SEGMENT_URL}/{slope_id}/details"

    headers = {
        "Authorization": f"Bearer {bearer_token}",
        "Content-Type": "application/json",
    }

    is_segment = False
    try:
        async with session.get(slope_url, headers=headers) as response:
            _LOGGER.debug(f"Trying to get {slope_url}")
            if response.status == 401:
                _LOGGER.error(f"Error 401 for {slope_url}")
                raise InvalidAuth
            elif response.status == 404:
                _LOGGER.info(f"Error 404 for {slope_url} - trying again with {segment_url}")
                # Try again with segment URL
                async with session.get(segment_url, headers=headers) as response:
                    if response.status == 401:
                        _LOGGER.error(f"Error 401 for {segment_url}")
                        raise InvalidAuth
                    _LOGGER.debug(f"Response {response.status} from {segment_url}")
                    response.raise_for_status()
                    api_data = await response.json()
                    is_segment = True
            else:
                _LOGGER.debug(f"Response {response.status} from {slope_url}")
                response.raise_for_status()
                api_data = await response.json()

            _LOGGER.debug(api_data)
            # Extract data from the new API structure (top-level fields)
            slope_name = api_data.get("name", f"Segment {api_data.get('selectedSegment', {}).get('id')}")
            if is_segment:
                route_api_id = api_data.get("selectedSegment", {}).get("id")
            else:
                route_api_id = api_data.get("id")

            # Verify the route exists and ID matches
            if route_api_id != int(slope_id):
                raise CannotConnect

            # Return route name for display
            return {
                "title": slope_name,
                "slope_name": slope_name,
                CONF_IS_SEGMENT: is_segment,
            }

    except aiohttp.ClientResponseError as err:
        if err.status == 401:
            raise InvalidAuth
        raise CannotConnect
    except aiohttp.ClientError as err:
        _LOGGER.error("Error connecting to Sporet API: %s", err)
        raise CannotConnect


class SporetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Sporet."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            user_input[CONF_BEARER_TOKEN] = sanitize_bearer_token(user_input[CONF_BEARER_TOKEN])
            user_input[CONF_SLOPE_ID] = sanitize_slope_id(user_input[CONF_SLOPE_ID])

            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Set unique ID based on slope_id
                await self.async_set_unique_id(user_input[CONF_SLOPE_ID])
                self._abort_if_unique_id_configured()
                user_input[CONF_IS_SEGMENT] = info[CONF_IS_SEGMENT]
                return self.async_create_entry(
                    title=info["title"],
                    data=user_input,
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SLOPE_ID): str,
                vol.Required(CONF_BEARER_TOKEN): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow for this handler."""
        return SporetOptionsFlowHandler()


class SporetOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Sporet options."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Validate the new bearer token
            test_data = {
                CONF_SLOPE_ID: self.config_entry.data[CONF_SLOPE_ID],
                CONF_BEARER_TOKEN: user_input[CONF_BEARER_TOKEN],
            }

            try:
                await validate_input(self.hass, test_data)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Update the config entry with the new bearer token
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data={
                        **self.config_entry.data,
                        CONF_BEARER_TOKEN: user_input[CONF_BEARER_TOKEN],
                    },
                )
                return self.async_create_entry(title="", data={})

        data_schema = vol.Schema(
            {
                vol.Required(
                    CONF_BEARER_TOKEN,
                    default=self.config_entry.data.get(CONF_BEARER_TOKEN, ""),
                ): str,
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=data_schema,
            errors=errors,
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
