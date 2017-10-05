#!/usr/bin/python3

import os
from setuptools import setup, find_packages


def get_requirements():
    requirements_txt = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'requirements.txt')
    with open(requirements_txt) as fd:
        return fd.read().splitlines()


setup(
    name='fabric8_analytics_webapp',
    version='0.1',
    packages=find_packages(),
    package_data={
        'f8a_webapp': [
            'swagger.yaml',
            os.path.join('static', 'html', '*.html'),
            os.path.join('static', 'js', '*.js'),
            os.path.join('static', 'css', '*.css')
        ]
    },
    scripts=['f8a-webapp.py'],
    install_requires=get_requirements(),
    include_package_data=True,
    author='Fridolin Pokorny',
    author_email='fridolin@redhat.com',
    maintainer='Fridolin Pokorny',
    maintainer_email='fridolin@redhat.com',
    description='fabric8-analytics Core job service',
    license='ASL 2.0',
    keywords='fabric8 analytics webapp',
    url='https://github.com/fabric8-analytics/fabric8-analytics-webapp',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Intended Audience :: Developers",
    ]
)
