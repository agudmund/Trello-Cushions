# utils/trello_api.py
import os
import time
import requests
from typing import Optional, Tuple

from utils.logging import log_message


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """Retrieve Trello API key and token from environment variables."""
    api_key = os.environ.get("TRELLO_KEY")
    token = os.environ.get("TRELLO_TOKEN")
    api_key = api_key.strip() if api_key else None
    token = token.strip() if token else None
    return api_key, token


def create_board(
    api_key: str,
    token: str,
    board_name: str = "Proofreading Kanban 🌱"
) -> Tuple[str, str]:
    """Create a new Trello board and return its ID and short URL."""
    url = "https://api.trello.com/1/boards/"
    data = {
        'key': api_key,
        'token': token,
        'name': board_name,
        'defaultLists': 'false',
        'prefs_background': 'blue'
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    board = response.json()
    log_message(f"Created board: {board['shortUrl']}")
    return board['id'], board['shortUrl']


def create_list(
    api_key: str,
    token: str,
    board_id: str,
    list_name: str = "To Review 🌅"
) -> str:
    """Create a new list on the specified board and return its ID."""
    url = "https://api.trello.com/1/lists"
    params = {
        'key': api_key,
        'token': token,
        'name': list_name,
        'idBoard': board_id,
        'pos': 'bottom'
    }
    response = requests.post(url, params=params)
    response.raise_for_status()
    log_message(f"Created list: {list_name}")
    return response.json()['id']


def create_card(
    api_key: str,
    token: str,
    list_id: str,
    card_name: str,
    desc: str,
    pos: str = 'bottom'
) -> bool:
    """Create a single card in the specified list. Returns True on success."""
    url = "https://api.trello.com/1/cards"
    params = {
        'key': api_key,
        'token': token,
        'idList': list_id,
        'name': card_name,
        'desc': desc,
        'pos': pos
    }
    response = requests.post(url, params=params)
    if response.status_code == 200:
        log_message(f"Added card: {card_name}")
        return True
    else:
        log_message(f"Failed to create card '{card_name}': {response.text}")
        return False