import logging
from typing import Any

import aiohttp

"""
HTTP client functions 
"""


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
    except aiohttp.client_exceptions.ClientConnectorError as e:
        logging.error(
            f"HTTP GET call to {url} using params {payload} raised a ClientConnectorError: '{e}' No result returned."
        )
        raise

