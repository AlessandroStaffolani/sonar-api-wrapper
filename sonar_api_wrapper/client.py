"""
SonarQube client api
"""
import os
from enum import Enum
from typing import Any, Optional, Union, List
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

DEFAULT_USERNAME = 'admin'
DEFAULT_PASSWORD = 'admin'
DEFAULT_SONAR_HOST_URL = 'http://localhost:9000/api/'


class RuleSeverity(str, Enum):
    INFO = 'INFO'
    MINOR = 'MINOR'
    MAJOR = 'MAJOR'
    CRITICAL = 'CRITICAL'
    BLOCKER = 'BLOCKER'


PAGINATION_MAX_SIZE = 500


def set_from_env(env_name: str, default_value: Optional[str], force_value: Optional[str] = None) -> str:
    if force_value is not None:
        return force_value
    if os.getenv(env_name) is not None:
        return os.getenv(env_name)
    else:
        return default_value


def get_auth_params(username: str, password: str, token: Optional[str] = None) -> HTTPBasicAuth:
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
        parameters: Optional[dict] = None,
        body: Optional[dict] = None,
        files: Any = None,
        headers: Optional[dict] = None,
        is_json: bool = True,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
        base_path: Optional[str] = None,
) -> Union[List[dict], dict, Any]:
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
        Argument value has precedence, followed by environment variable value and lastly default value is used.
    :param password: Password used for authentication.
        Default is set via the environment variable `SONAR_PASSWORD` or "admin".
        Argument value has precedence, followed by environment variable value and lastly default value is used.
    :param token: Token used for authentication. It overrides username and password if present.
        Default value is set via the environment variable `SONAR_AUTH_TOKEN` or None.
        Argument value has precedence, followed by environment variable value and lastly default value is used.
    :param base_path: The base endpoint used to build the API call.
        Default is set via the environment variable `SONAR_HOST_URL` or "http://localhost:9000/api/".
        Argument value has precedence, followed by environment variable value and lastly default value is used.
    :return: Returns the API response as `list[dict]`, `dict`,
        or any other type based on the response content or raises an exception.
        ### Example

        ```python
        import os

        from sonar_api_wrapper import api_call

        # override default access config
        os.environ['SONAR_PASSWORD'] = 'Username'
        os.environ['SONAR_PASSWORD'] = 'YourPassword'
        os.environ['SONAR_HOST_URL'] = 'https://yours.sonarqube/api/'

        response = api_call('GET', 'qualityprofiles/search', parameters={
            'defaults': 'true'
        })

        print(f'{response["projects"] = }')
        ```

        ### Exceptions

        Exceptions are raised based on HTTP errors or other request issues.
    """

    sonar_username = set_from_env('SONAR_USERNAME', DEFAULT_USERNAME, username)
    sonar_password = set_from_env('SONAR_PASSWORD', DEFAULT_PASSWORD, password)
    sonar_token = set_from_env('SONAR_AUTH_TOKEN', None, token)
    sonar_base_path = set_from_env('SONAR_HOST_URL', DEFAULT_SONAR_HOST_URL, base_path)

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
        username: Optional[str] = None,
        password: Optional[str] = None,
        base_path: Optional[str] = None,
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
        username: Optional[str] = None,
        base_path: Optional[str] = None,
) -> None:
    parameters = {
        'login': username,
        'previousPassword': old_password,
        'password': new_password
    }
    api_call('POST', 'users/change_password', parameters,
             password=old_password, username=username, base_path=base_path)
