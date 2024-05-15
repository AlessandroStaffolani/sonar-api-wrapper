# Sonar API Wrapper

Sonar API Wrapper - a Sonarqube api wrapper

## Install

```bash
pip install sonar-api-wrapper
``` 

## How to use

### api_call

Executes an API call to SonarQube. This method wraps the `requests.request` method.

### Parameters

- `method` (`str`): HTTP method to use (e.g., GET, POST, etc.).
- `route` (`str`): API path that will be concatenated with `base_path`. For example, `qualityprofiles/search`.
- `parameters` (`dict` | `None`): Dictionary of parameters for the API call. Default is `None`.
- `body` (`dict` | `None`): Body of the request. Default is `None`.
- `files` (`Any`): Files to be sent in the request. Default is `None`.
- `headers` (`dict` | `None`): Headers of the request. Default is `None`.
- `is_json` (`bool`): If set to `True`, the response will be parsed as JSON. Otherwise, it returns the decoded content. Default is `True`.
- `username` (`str` | `None`): Username used for authentication. Default is set via the environment variable `SONAR_USERNAME` or "admin". Argument value has precedence, followed by environment variable value and lastly default value is used.
- `password` (`str` | `None`): Password used for authentication. Default is set via the environment variable `SONAR_PASSWORD` or "admin". Argument value has precedence, followed by environment variable value and lastly default value is used.
- `token` (`str` | `None`): Token used for authentication. It overrides username and password if present. Default value is set via the environment variable `SONAR_TOKEN` or None. Argument value has precedence, followed by environment variable value and lastly default value is used.
- `base_path` (`str` | `None`): The base endpoint used to build the API call. Default is set via the environment variable `SONAR_ENDPOINT` or "http://localhost:9000/api/". Argument value has precedence, followed by environment variable value and lastly default value is used.

### Returns

Returns the API response as `list[dict]`, `dict`, or any other type based on the response content or raises an exception.

### Example

```python
import os

from sonar_api_wrapper import api_call

# override default access config
os.environ['SONAR_PASSWORD'] = 'Username'
os.environ['SONAR_PASSWORD'] = 'YourPassword'
os.environ['SONAR_ENDPOINT'] = 'https://yours.sonarqube/api/'

response = api_call('GET', 'qualityprofiles/search', parameters={
    'defaults': 'true'
})

print(f'{response["projects"] = }')
```

### Exceptions

Exceptions are raised based on HTTP errors or other request issues.

## Develop

### Install - Dev

The dev install is only required if additional development is needed for this library

```bash
pip install -e '.[dev]'
```

### Build the library

Run the command:

```bash
python -m build -w
```

### Publish the library

```bash
python -m twine upload dist/*
```

### Test the library

Run the test with command:

```bash
pytest
```
