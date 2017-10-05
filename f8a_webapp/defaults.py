#!/usr/bin/env python3
import os
from datetime import timedelta

_BAYESIAN_WEBAPP_DIR = os.path.dirname(os.path.realpath(__file__))

DEFAULT_SERVICE_PORT = 35000
STATIC_DIR = os.getenv('F8A_WEBAPP_STATIC_DIR', os.path.join(_BAYESIAN_WEBAPP_DIR, 'static'))
SWAGGER_YAML_PATH = os.path.join(_BAYESIAN_WEBAPP_DIR, 'swagger.yaml')
TOKEN_VALID_TIME = timedelta(days=14)
AUTH_ORGANIZATION = 'fabric8-analytics'
GITHUB_CONSUMER_KEY = os.environ.get('GITHUB_CONSUMER_KEY', 'not-set')
GITHUB_CONSUMER_SECRET = os.environ.get('GITHUB_CONSUMER_SECRET', 'not-set')
GITHUB_ACCESS_TOKENS = os.environ.get('GITHUB_ACCESS_TOKENS', '').split(',')
APP_SECRET_KEY = os.environ.get('APP_SECRET_KEY', 'not-set')

# keep disabled authentication by default
DISABLE_AUTHENTICATION = os.getenv('DISABLE_AUTHENTICATION', '1') in ('1', 'True', 'true')
