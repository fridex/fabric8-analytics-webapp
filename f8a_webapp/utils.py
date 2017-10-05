#!/usr/bin/env python3
import logging
from functools import wraps
import requests
import random
from flask import request, abort
import f8a_webapp.defaults as configuration
from f8a_webapp.models import WebappToken
from f8a_webapp.error import TokenExpired
from selinon import run_flow_selective

logger = logging.getLogger(__name__)


def webapp_run_flow_selective(flow_name, node_args, task_names):
    logger.info("Scheduling selective Selinon flow '%s' with node_args=%s and task_names=%s")
    return run_flow_selective(flow_name, node_args, task_names)


def webapp_run_flow(flow_name, node_args):
    logger.info("Scheduling Selinon flow '%s' with node_args=%s")
    return run_flow_selective(flow_name, node_args)


def requires_auth(func):
    """Verify authentication token sent in header.

    :param func: function that should be called if verification succeeds
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        if configuration.DISABLE_AUTHENTICATION:
            return func(*args, **kwargs)

        auth_token = request.headers.get('auth_token')
        try:
            if not WebappToken.verify(auth_token):
                logger.info("Verification for token '%s' failed", auth_token)
                abort(401)
        except TokenExpired:
            abort(401, "Token has expired, logout and generate a new one")

        return func(*args, **kwargs)

    return wrapper


def is_organization_member(user_data):
    """ Check that a user is a member of organization

    :param user_data: user OAuth data
    :return: True if user is a member of organization
    """
    data = requests.get(user_data['organizations_url'], params={'access_token': get_gh_token()})
    data.raise_for_status()
    return any(org_def['login'] == configuration.AUTH_ORGANIZATION for org_def in data.json())


def get_gh_token():
    return random.choice(configuration.GITHUB_ACCESS_TOKENS).strip()
