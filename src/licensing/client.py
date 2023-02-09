import requests
import logging


def http_get(url: str, payload: dict) -> requests.Response:
    """
    Sends a GET request to an external API
    :param url: the url to call
    :param payload: optional parameters as a dict
    """
    try:
        response = requests.get(url, params=payload)
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
