#!/usr/bin/env python3

import logging

from flask import session, url_for, request
from selinon import run_flow, StoragePool

import f8a_webapp.defaults as defaults
from f8a_webapp.auth import github
from f8a_webapp.utils import requires_auth
from f8a_webapp.utils import webapp_run_flow_selective
from f8a_webapp.utils import webapp_run_flow
from f8a_webapp.utils import is_organization_member
from f8a_webapp.models import WebappToken

logger = logging.getLogger(__name__)


def generate_token():
    return github.authorize(callback=url_for('/api/v1.f8a_webapp_api_v1_authorized', _external=True))


def logout():
    if 'auth_token' not in session:
        return {}, 401

    session.pop('auth_token')
    return {}, 201


def authorized():
    if 'auth_token' in session and isinstance(session['auth_token'], tuple) and session['auth_token']:
        return WebappToken.get_info(session.get('auth_token', (None,))[0])

    logger.info("Authorized redirection triggered, getting authorized response from Github")
    resp = github.authorized_response()
    logger.info("Got Github authorized response")

    if resp is None or resp.get('access_token') is None:
        msg = 'Access denied: reason=%s error=%s resp=%s' % (
            request.args['error'],
            request.args['error_description'],
            resp
        )
        logger.warning(msg)
        return {'error': msg}, 400

    logger.debug("Assigning authorization token '%s' to session", resp['access_token'])
    session['auth_token'] = (resp['access_token'], '')
    oauth_info = github.get('user')
    if not is_organization_member(oauth_info.data):
        logger.debug("User '%s' is not member of organization '%s'",
                     oauth_info.data['login'], defaults.AUTH_ORGANIZATION)
        logout()
        return {'error': 'unauthorized'}, 401

    token_info = WebappToken.store_token(oauth_info.data['login'], resp['access_token'])
    return token_info


def get_liveness():
    # TODO: RDS connection
    logger.warning("Liveness probe - trying to schedule the livenessFlow")
    run_flow('livenessFlow', {})
    logger.warning("Liveness probe - finished")
    return {}, 200


def get_readiness():
    return {}, 200


@requires_auth
def get_project_analysis(ecosystem, name, analysis):
    s3 = StoragePool.get_connected_storage('S3PackageData')

    try:
        result = s3.retrieve_task_result(ecosystem, name, task_name=analysis)
    except Exception as exc:
        # TODO: implement error handling based on exceptions raised
        logger.exception("Failed to get project analysis "
                         "for '{ecosystem}'/'{name}'".format(**locals()))
        return {'error': str(exc)}, 400

    return {
        'ecosystem': ecosystem,
        'name': name,
        'analysis': analysis,
        'result': result
    }


@requires_auth
def get_project_analysis_listing(ecosystem, name):
    s3 = StoragePool.get_connected_storage('S3PackageData')

    try:
        analyses = s3.list_available_task_results({'ecosystem': ecosystem, 'name': name})
    except Exception as exc:
        # TODO: implement error handling based on exceptions raised
        logger.exception("Failed to get project analysis listing for "
                         "'{ecosystem}'/'{name}'".format(**locals()))
        return {'error': str(exc)}, 400

    return {
        'ecosystem': ecosystem,
        'name': name,
        'analyses': analyses
    }


@requires_auth
def get_project_listing(ecosystem, prefix=None):
    s3 = StoragePool.get_connected_storage('S3PackageData')

    try:
        projects = s3.list_available_names(ecosystem, prefix=prefix)
    except Exception as exc:
        # TODO: implement error handling based on exceptions raised
        logger.exception("Failed to list projects "
                         "for '{ecosystem}'".format(**locals()))
        return {'error': str(exc)}, 400

    return {
        'ecosystem': ecosystem,
        'projects': projects
    }


@requires_auth
def post_package_analysis(ecosystem, name, version, analysis=None):
    node_args = {
        'ecosystem': ecosystem,
        'name': name,
        'version': version
    }

    if analysis:
        task_names = analysis.split(',')
        for task_name in task_names:
            if task_name[0].isupper():
                return {'error': 'Invalid analysis name: %s' % task_name}, 404

        if 'PackageGraphResultCollector' not in task_names:
            task_names.append('PackageGraphResultCollector')

        if 'GraphResultCollector' not in task_names:
            task_names.append('GraphResultCollector')

        dispatcher_id = webapp_run_flow_selective('bayesianFlow',
                                                  node_args=node_args,
                                                  task_names=task_names)
    else:
        dispatcher_id = webapp_run_flow('bayesianFlow', node_args)

    logger.info("Scheduled flow served by dispatcher '%s'", dispatcher_id)

    return {}, 201


@requires_auth
def post_project_analysis(ecosystem, name, analysis=None, url=None):
    node_args = {
        'ecosystem': ecosystem,
        'name': name,
        'url': url
    }

    # TODO: check if the given project exists, if no return error because we don't have remote URL
    if analysis:
        task_names = analysis.split(',')
        for task_name in task_names:
            if task_name[0].isupper():
                return {'error': 'Invalid analysis name: %s' % task_name}, 404

        if 'PackageGraphResultCollector' not in task_names:
            task_names.append('PackageGraphResultCollector')

        dispatcher_id = webapp_run_flow_selective('bayesianPackageFlow',
                                                  node_args=node_args,
                                                  task_names=task_names)
    else:
        dispatcher_id = webapp_run_flow('bayesianPackageFlow', node_args=node_args)

    logger.info("Scheduled flow served by dispatcher '%s'", dispatcher_id)

    return {}, 201


@requires_auth
def get_package_analysis(ecosystem, name, version, analysis):
    s3 = StoragePool.get_connected_storage('S3Data')

    try:
        result = s3.retrieve_task_result(ecosystem, name, version, task_name=analysis)
    except Exception as exc:
        # TODO: implement proper exception handling with descriptive error message
        logger.exception("Failed to get package analysis "
                         "for '{ecosystem}'/'{name}'/'{version}'".format(**locals()))
        return {'error': str(exc)}, 400

    return {
        'ecosystem': ecosystem,
        'name': name,
        'version': version,
        'analysis': analysis,
        'result': result
    }


@requires_auth
def get_package_analysis_listing(ecosystem, name, version):
    s3 = StoragePool.get_connected_storage('S3Data')

    try:
        analyses = s3.list_available_task_results({'ecosystem': ecosystem, 'name': name, 'version': version})
    except Exception as exc:
        # TODO: implement proper exception handling with descriptive error message
        logger.exception("Failed to list package analyses "
                         "for '{ecosystem}'/'{name}'/'{version}'".format(**locals()))
        return {'error': str(exc)}, 400

    return {
        'ecosystem': ecosystem,
        'name': name,
        'version': version,
        'analyses': analyses
    }


@requires_auth
def get_package_version_listing(ecosystem, name):
    s3 = StoragePool.get_connected_storage('S3Data')

    try:
        versions = s3.list_available_versions({'ecosystem': ecosystem, 'name': name})
    except Exception as exc:
        # TODO: implement proper exception handling with descriptive error message
        logger.exception("Failed to list available versions "
                         "for '{ecosystem}'/'{name}/'".format(**locals()))
        return {'error': str(exc)}, 400

    return {
        'ecosystem': ecosystem,
        'name': name,
        'versions': versions,
    }


@requires_auth
def get_package_listing(ecosystem, prefix=None):
    s3 = StoragePool.get_connected_storage('S3Data')

    try:
        packages = s3.list_available_names(ecosystem, prefix=prefix)
    except Exception as exc:
        # TODO: implement proper exception handling with descriptive error message
        logger.exception("Failed to list available names "
                         "for '{ecosystem}'".format(ecosystem=ecosystem))
        return {'error': str(exc)}, 400

    return {
        'ecosystem': ecosystem,
        'packages': packages
    }


def get_ecosystem_listing():
    # TODO: implement using RDS
    return {'error': 'Not implemented yet'}, 418
