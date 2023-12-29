"""
This module is responsible for handling the local files.
"""
from enum import Enum
import os
import pickle

EXCLUDED_USERS_PATH = 'config/excluded'
ARTICLES_PATH = 'data/{}/articles.pkl'

class ExcludedReturnType(Enum):
    """Enum used to handle the return type of the excluded users function."""
    FULL = "FULL"
    IDS = "USERNAMES"
    NAMES = "NAMES"

def get_articles_from_local(user):
    """Gets the articles saved in user local file."""
    with open(ARTICLES_PATH.format(user), 'rb') as f:
        return pickle.load(f)

def save_articles_to_local(user, data):
    """Saves the articles data into a local pkl file."""
    with open(ARTICLES_PATH.format(user), 'wb') as f:
        pickle.dump(data, f)

def append_and_save_articles_to_local(user, append_to, to_append):
    """Appends the new articles to the current list and save it locally."""
    for guid in to_append:
        append_to.append({'guid': guid, 'clapped': False})
    save_articles_to_local(user, append_to)

def get_excluded_users(return_type: ExcludedReturnType = ExcludedReturnType.FULL):
    """
    Get the list of excluded users.
    By default, returns a list of <username, name>,  but can be changed specifying a return_type.
    """
    with open(EXCLUDED_USERS_PATH, 'r', encoding='utf-8') as f:
        users_excluded = f.readlines()
    users = [user.rstrip() for user in users_excluded]

    if return_type == ExcludedReturnType.IDS:
        return [user.split(',')[0] for user in users]
    if return_type == ExcludedReturnType.NAMES:
        return [user.split(',')[1] for user in users]
    return users

def check_data_directory(user):
    """Checks if data/{user} directory exists. If not, it'll be created."""
    os.makedirs(f'data/{user}', exist_ok=True)

def local_articles_file_exists(user):
    """Checks if the pkl file exists for given user."""
    return os.path.exists(ARTICLES_PATH.format(user))
