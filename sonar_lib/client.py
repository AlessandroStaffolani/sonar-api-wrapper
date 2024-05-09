"""
SonarQube client api
"""
import os
from enum import Enum
from typing import Any
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'
DEFAULT_SONAR_ENDPOINT = 'http://localhost:9000/api/'


class RuleSeverity(str, Enum):
    INFO = 'INFO'
    MINOR = 'MINOR'
    MAJOR = 'MAJOR'
    CRITICAL = 'CRITICAL'
    BLOCKER = 'BLOCKER'


def set_from_env(env_name: str, default_value: str) -> str:
    if os.getenv(env_name) is not None:
        return os.getenv(env_name)
    else:
        return default_value


def get_auth_params(username: str, password: str) -> HTTPBasicAuth:
    return HTTPBasicAuth(username=username, password=password)


def build_endpoint(path: str, base_path: str) -> str:
    return urljoin(base_path, path)


def api_call(
        method: str,
        route: str,
        parameters: dict | None = None,
        body: dict | None = None,
        files: Any = None,
        headers: dict | None = None,
        username: str | None = DEFAULT_USERNAME,
        password: str | None = DEFAULT_PASSWORD,
        is_json: bool = True,
        base_path: str | None = DEFAULT_SONAR_ENDPOINT,
) -> list[dict] | dict | Any:

    sonar_username = set_from_env('SONAR_USERNAME', username)
    sonar_password = set_from_env('SONAR_PASSWORD', password)
    sonar_base_path = set_from_env('DEFAULT_SONAR_ENDPOINT', base_path)

    response = requests.request(
        method=method,
        url=build_endpoint(route, sonar_base_path),
        data=body,
        params=parameters,
        headers=headers,
        files=files,
        auth=get_auth_params(sonar_username, sonar_password)
    )
    if response.status_code == 200:
        if is_json:
            return response.json()
        else:
            return response.content.decode()
    else:
        return response.raise_for_status()


def check_sonar_status(
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        base_path: str = DEFAULT_SONAR_ENDPOINT
) -> bool:
    ready = False
    try:
        response = api_call('GET', 'system/status', username=username, password=password, base_path=base_path)
        if response is not None and 'status' in response and response['status'] == 'UP':
            ready = True
        else:
            ready = False
        return ready
    except Exception as _:
        return ready


def update_password(
        old_password: str,
        new_password: str,
        username: str = DEFAULT_USERNAME,
        base_path: str = DEFAULT_SONAR_ENDPOINT,
) -> None:
    parameters = {
        'login': username,
        'previousPassword': old_password,
        'password': new_password
    }
    api_call('POST', 'users/change_password', parameters,
             password=old_password, username=username, base_path=base_path)
