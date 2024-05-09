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
    if not base_path.endswith('/'):
        base_path = f'{base_path}/'
    if path.startswith('/'):
        path = path[1:]
    return urljoin(base_path, path)


def api_call(
        method: str,
        route: str,
        parameters: dict | None = None,
        body: dict | None = None,
        files: Any = None,
        headers: dict | None = None,
        is_json: bool = True,
        username: str | None = DEFAULT_USERNAME,
        password: str | None = DEFAULT_PASSWORD,
        base_path: str | None = DEFAULT_SONAR_ENDPOINT,
) -> list[dict] | dict | Any:
    """
    Execute an api call to sonarqube, the method wraps the request.request method
    :param method: http method: GET, POST, etc.
    :param route: api path that will be concatenated with the base_path. e.g. qualityprofiles/search
    :param parameters: dictionary of parameters of the api call
    :param body: body of the request
    :param files: files of the request
    :param headers: headers of the request
    :param is_json: if set to True (the default) it will parse the response as a json,
        otherwise it returns the decoded content
    :param username: username used to log (should be the token if accessing via token).
        Default value "admin", can also be set via the environment variable SONAR_USERNAME
    :param password: password used to log (should be empty if accessing via token).
        Default value "admin", can also be set via the environment variable SONAR_PASSWORD
    :param base_path: the base endpoint used to build the api call.
        Default: "http://localhost:9000/api/" can also be set via the environment variable DEFAULT_SONAR_ENDPOINT
    :return: the api response or raise the exception
    """

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
