from aiohttp import ClientSession, ClientTimeout

from .constants import HEADERS


def get_client_session() -> ClientSession:
    timeout = ClientTimeout(30)
    return ClientSession(timeout=timeout, headers=HEADERS)
