# Qabel Accounting Server

[![Build Status](https://travis-ci.org/Qabel/qabel-accounting.svg?branch=master)](https://travis-ci.org/Qabel/qabel-accounting)

## Requirements
Python 3.4 or 3.5

## Installation

Create a virtualenv for the project

	virtualenv -p python3.4 ../venv
	source ../venv/bin/activate
	pip install -r requirements.txt

Run the migrations

	./manage.py migrate

## Running tests

The tests are run by the py.test framework. You can choose which browser you want to use for the functional tests.

Phantomjs: (recommended)

	py.test --splinter-webdriver phantomjs

Firefox:

	py.test --splinter-webdriver firefox

## Production setup

See the [django documentation](https://docs.djangoproject.com/en/1.8/howto/deployment/)
The server exports [prometheus](https://www.prometheus.io) metrics at /metrics. If those should not be public, you should
block this location in the webserver.
If you have problems with CORS (Cross-Origin Resource Sharing), edit the 'CORS_ORIGIN_WHITELIST' in local_settings.py. For more information see [CORS middleware configuration options](https://github.com/zestedesavoir/django-cors-middleware#configuration).

## Development

To use the dummy mail backend, see: [django documentation for email](https://docs.djangoproject.com/en/1.9/topics/email/#dummy-backend)

Insert this line in qabel_id/settings.py :

    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

In your django settings you have to set an API_SECRET that should be known only by the
qabel-block server.
