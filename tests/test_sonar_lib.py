from xml.etree import ElementTree

import pytest
from requests import HTTPError

from sonar_lib import api_call


def test_get_request(start_sonarqube) -> None:
    response = api_call('GET', 'qualityprofiles/search', parameters={
        'defaults': 'true'
    })

    assert len(response['profiles']) > 0


def test_post_request(start_sonarqube) -> None:
    test_project_name = 'Test Project'
    test_project_key = 'test.project'
    response = api_call('POST', 'projects/create', parameters={
        'name': test_project_name,
        'project': test_project_key
    })

    assert response['project']['key'] == test_project_key
    assert response['project']['name'] == test_project_name


def test_not_json_response(start_sonarqube) -> None:
    language = 'ts'
    response = api_call('GET', 'qualityprofiles/search', parameters={
        'defaults': 'true',
        'language': language
    })

    profile_name = response['profiles'][0]['name']

    content = api_call('GET', 'qualityprofiles/backup', parameters={
        'language': language,
        'qualityProfile': profile_name
    }, is_json=False)

    content_xml = ElementTree.fromstring(content)
    response_profile_name = content_xml.find('.//name').text
    response_profile_lang = content_xml.find('.//language').text

    assert profile_name == response_profile_name
    assert language == response_profile_lang


def test_request_error(start_sonarqube) -> None:
    with pytest.raises(HTTPError):
        api_call('GET', 'qualityprofiles/backup', parameters={}, is_json=True)

