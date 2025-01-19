from typing import Dict

from common.logger import get_logger

log = get_logger(__name__)

def parse_cookies(cookies: str) -> Dict[str, str]:
    """Parse cookies from a string to a dictionary."""
    log.debug(f'Parsing cookies: {cookies}')
    return dict([cookie for cookie in [cookie.split('=') for cookie in cookies.split('; ')] if len(cookie) == 2])

def serialize_cookies(cookies: Dict[str, str]) -> str:
    """Serialize cookies from a dictionary to a string."""
    return '; '.join([f'{key}={value}' for key, value in cookies.items()])
