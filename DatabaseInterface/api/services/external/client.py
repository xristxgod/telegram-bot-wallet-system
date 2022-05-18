from typing import Optional, Union, Dict, List

import requests

from config import logger

class Client:
    @staticmethod
    def get_request(url: str) -> Optional[Union[Dict, List]]:
        try:
            data = requests.request('GET', url)
            return data.json()
        except Exception as error:
            logger.error(f"ERROR: {error}")