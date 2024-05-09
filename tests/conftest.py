import os
import subprocess
import sys
import time

import pytest

from sonar_api_wrapper import DEFAULT_USERNAME, DEFAULT_PASSWORD, DEFAULT_SONAR_ENDPOINT
from sonar_api_wrapper.client import check_sonar_status, update_password


def wait_for_sonar(
        max_wait: int = 60,
        sleep: int = 1,
        username: str = DEFAULT_USERNAME,
        password: str = DEFAULT_PASSWORD,
        base_path: str = DEFAULT_SONAR_ENDPOINT,
) -> None:
    waited = 0
    is_ready = check_sonar_status(username, password, base_path)
    while not is_ready and waited < max_wait:
        time.sleep(sleep)
        is_ready = check_sonar_status(username, password, base_path)
        waited += sleep

    if not is_ready:
        raise TimeoutError(f'Sonarqube not ready after {max_wait} seconds')


def stop_container(container_id: str) -> None:
    command = [
        "docker", "stop", container_id
    ]
    stop_result = subprocess.run(command, capture_output=True, text=True)
    if stop_result.returncode != 0:
        raise RuntimeError(f'Error stopping Sonarqube test container: {stop_result.stderr.strip()}')


@pytest.fixture(scope='session')
def start_sonarqube() -> str:
    image_name = "sonarqube:9.9.4-community"
    command = [
        "docker", "run", "--rm", "-d", "-p", "9999:9000", image_name
    ]

    start_result = subprocess.run(command, capture_output=True, text=True)

    if start_result.returncode == 0:
        container_id = start_result.stdout.strip()
        try:
            os.environ['SONAR_ENDPOINT'] = 'http://localhost:9999/api'

            wait_for_sonar()

            sonar_test_password = 'password123'
            update_password(DEFAULT_PASSWORD, sonar_test_password)

            os.environ['SONAR_PASSWORD'] = sonar_test_password
            yield sonar_test_password
        except Exception as e:
            sys.stderr.write('Errors during execution of test')
            raise e
        finally:
            stop_container(container_id)
    else:
        raise RuntimeError(f'Error starting Sonarqube test container: {start_result.stderr.strip()}')
