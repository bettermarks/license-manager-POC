import logging
from typing import Any
from urllib.parse import urljoin, quote_plus

import aiohttp

from licensing.utils import async_measure_time


def multi_urljoin(*parts):
    """helper: joins multiple URL parts"""
    return urljoin(parts[0], "/".join(quote_plus(part.strip("/"), safe="/") for part in parts[1:]))


async def http_get(url: str, payload: dict | None = None) -> Any:
    """
    Sends a GET request to an external API
    :param url: the url to call
    :param payload: optional parameters as a dict
    """
    try:
        async with aiohttp.ClientSession() as session:
            # TODO
            # headers={
            # "x-api-key": settings.EVENT_SERVICE_API_KEY,
            # "Content-type": "application/json",
            # }

            async with session.get(url, params=payload) as response:
                if not response.ok:
                    raise Exception(f"Response status {response.status}.")
                return await response.json()
    # Exception handling for the 'bad' cases.
    except Exception as e:
        logging.error(
            f"HTTP GET call to {url} using params {payload} raised an Exception: '{e}' No result returned."
        )
        raise


# TODO use some security mechanism to call the HP API (maybe an API key)
@async_measure_time
async def get_user_memberships_from_provider(url: str, user_eid: str) -> list:
    """Calls the hierarchy provider URL and returns the membership list for the given user EID"""
    return await http_get(multi_urljoin(url + "/", "users", user_eid, "membership"))
