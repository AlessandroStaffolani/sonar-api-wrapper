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


def get_auth_params(username: str, password: str, token: str | None = None) -> HTTPBasicAuth:
    if token is None:
        return HTTPBasicAuth(username=username, password=password)
    else:
        return HTTPBasicAuth(username=token, password='')


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
        token: str | None = None,
        base_path: str | None = DEFAULT_SONAR_ENDPOINT,
) -> list[dict] | dict | Any:
    """
    Execute an api call to sonarqube, the method wraps the request.request method
    :param method: HTTP method to use (e.g., GET, POST, etc.).
    :param route: API path that will be concatenated with `base_path`. For example, `qualityprofiles/search`.
    :param parameters: Dictionary of parameters for the API call. Default is `None`.
    :param body: Body of the request. Default is `None`.
    :param files: Files to be sent in the request. Default is `None`.
    :param headers: Headers of the request. Default is `None`.
    :param is_json: If set to `True`, the response will be parsed as JSON.
        Otherwise, it returns the decoded content. Default is `True`.
    :param username: Username used for authentication.
        Default is set via the environment variable `SONAR_USERNAME` or "admin".
    :param password: Password used for authentication.
        Default is set via the environment variable `SONAR_PASSWORD` or "admin".
    :param token: Token used for authentication. It overrides username and password if present.
        Default value is set via the environment variable `SONAR_TOKEN` or None.
    :param base_path: The base endpoint used to build the API call.
        Default is set via the environment variable `DEFAULT_SONAR_ENDPOINT` or "http://localhost:9000/api/".
    :return: Returns the API response as `list[dict]`, `dict`,
        or any other type based on the response content or raises an exception.
        ### Example

        ```python
        import os

        from sonar_api_wrapper import api_call

        # override default access config
        os.environ['SONAR_PASSWORD'] = 'Username'
        os.environ['SONAR_PASSWORD'] = 'YourPassword'
        os.environ['DEFAULT_SONAR_ENDPOINT'] = 'https://yours.sonarqube/api/'

        response = api_call('GET', 'qualityprofiles/search', parameters={
            'defaults': 'true'
        })

        print(f'{response["projects"] = }')
        ```

        ### Exceptions

        Exceptions are raised based on HTTP errors or other request issues.
    """

    sonar_username = set_from_env('SONAR_USERNAME', username)
    sonar_password = set_from_env('SONAR_PASSWORD', password)
    sonar_token = set_from_env('SONAR_TOKEN', token)
    sonar_base_path = set_from_env('SONAR_ENDPOINT', base_path)

    response = requests.request(
        method=method,
        url=build_endpoint(route, sonar_base_path),
        data=body,
        params=parameters,
        headers=headers,
        files=files,
        auth=get_auth_params(sonar_username, sonar_password, sonar_token)
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
