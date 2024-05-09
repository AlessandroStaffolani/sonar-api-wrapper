import os


build_id = os.getenv('BUILD_ID') if os.getenv('BUILD_ID') is not None else ''


__title__ = "sonar-lib"
__description__ = "Python wrapper for Sonarqube REST API"
# __url__ = "https://requests.readthedocs.io"
__version__ = f"0.0.1{build_id}"
__author__ = "Alessandro Staffolani"
__author_email__ = "alestam93@gmail.com"
# __license__ = "Apache 2.0"
# __copyright__ = "Copyright Kenneth Reitz"
