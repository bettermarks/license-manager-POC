from typing import Any

import requests
import logging

from urllib.parse import urljoin, quote_plus


def multi_urljoin(*parts):
    """helper"""
    print("parts[0]", parts[0])
    print("parts rest", "/".join(quote_plus(part.strip("/"), safe="/") for part in parts[1:]))
    return urljoin(parts[0], "/".join(quote_plus(part.strip("/"), safe="/") for part in parts[1:]))


async def http_get(url: str, payload: dict | None = None) -> requests.Response:
    """
    Sends a GET request to an external API
    :param url: the url to call
    :param payload: optional parameters as a dict
    """
    try:
        response = requests.get(
            url,
            params=payload,
            # headers={     # TODO
                # "x-api-key": settings.EVENT_SERVICE_API_KEY,
                # "Content-type": "application/json",
            # }
        )
        if not response.ok:
            logging.error(
                f"HTTP GET call raised an error",
                url=url,
                params=payload,
                status_code=response.status_code
            )
        return response
    # Exception handling for the 'bad' cases.
    except Exception as e:
        logging.error(
            f"HTTP GET call to {url} using params {payload} raised an Exception: '{e}' No result returned."
        )
        raise


async def get_hierarchy(url: str, user_eid: str) -> Any:
    """Calls the hierarchy provider URL and returns the hierarchy for the given user EID"""
    # TODO use some security mechanism to call the HP API (maybe an API key)
    return (await http_get(multi_urljoin(url + "/", "users", user_eid))).json()
