<img align="left" width="0" height="150px" hspace="20"/>
<a href="https://qabel.de" align="left">
	<img src="https://files.qabel.de/img/qabel_logo_orange_preview.png" height="150px" align="left"/>
</a>
<img align="left" width="0" height="150px" hspace="25"/>
> The Qabel Accounting Server

[![Build Status](https://travis-ci.org/Qabel/qabel-accounting.svg?branch=master)](https://travis-ci.org/Qabel/qabel-accounting)
[![version](https://img.shields.io/badge/beta-dev-blue.svg)](https://qabel.de)

This project provides the accounting server for <a href="https://qabel.de"><img alt="Qabel" src="https://files.qabel.de/img/qabel-kl.png" height="18px"/></a> that manages Qabel-Accounts that authorize Qabel Box usage according to the [Qabel Box Protocol](http://qabel.github.io/docs/Qabel-Protocol-Box/).

<br style="clear: both"/>
<br style="clear: both"/>
<p align="center">
	<a href="#introduction">Introduction</a> |
	<a href="#installation">Installation</a> |
	<a href="#requirements">Requirements</a> |
	<a href="#running_tests">Running the tests</a> |
	<a href="#running_server">Running the server</a> |
	<a href="#production_setup">Production setup</a> |
	<a href="#development">Development</a>
</p>

# Introduction
For a comprehensive documentation of the whole Qabel Platform use https://qabel.de as the main source of information. http://qabel.github.io/docs/ may provide additional technical information.

Qabel consists of multiple Projects:
 * [Qabel Android Client](https://github.com/Qabel/qabel-android)
 * [Qabel Desktop Client](https://github.com/Qabel/qabel-desktop)
 * [Qabel Core](https://github.com/Qabel/qabel-core) is a library that includes the common code between both clients to keep them consistent
 * [Qabel Drop Server](https://github.com/Qabel/qabel-drop) is the target server for drop messages according to the [Qabel Drop Protocol](http://qabel.github.io/docs/Qabel-Protocol-Drop/)
 * [Qabel Accounting Server](https://github.com/Qabel/qabel-accounting) manages Qabel-Accounts that authorize Qabel Box usage according to the [Qabel Box Protocol](http://qabel.github.io/docs/Qabel-Protocol-Box/)
 * [Qabel Block Server](https://github.com/Qabel/qabel-block) serves as the storage backend according to the [Qabel Box Protocol](http://qabel.github.io/docs/Qabel-Protocol-Box/)

## Requirements
* Python 3.5 (+virtualenv)
* Redis
* PostgreSQL (for production setup only)
* Mail server (for production setup only)

## Installation

Create a virtualenv for the project

	virtualenv -p python3.5 ../venv
	source ../venv/bin/activate
	pip install -r requirements.txt

(optional) For production setup do

	export DJANGO_SETTINGS_MODULE=qabel_id.settings.production_settings
	copy qabel_id/settings/local_settings.example.py to local_settings.py and adapt it (see below)

(optional) Adapting settings

	Change SECRET_KEY and keep it save
	Change API_SECRET and share it with block server
	Change database settings accordingly to your needs
	Change email settings accordingly to your needs

Run the migrations

	./manage.py migrate

## <a name="running_tests"></a>Running tests

The tests are run by the py.test framework. You can choose which browser you want to use for the functional tests.

Phantomjs: (recommended)

	py.test --splinter-webdriver phantomjs

Firefox:

	py.test --splinter-webdriver firefox
	
## <a name="running_server"></a>Running the server
```bash
python manage.py runserver
```

## <a name="production_setup"></a>Production setup

See the [django documentation](https://docs.djangoproject.com/en/1.8/howto/deployment/)
The server exports [prometheus](https://www.prometheus.io) metrics at /metrics. If those should not be public, you should
block this location in the webserver.
If you have problems with CORS (Cross-Origin Resource Sharing), edit the 'CORS_ORIGIN_WHITELIST' in local_settings.py. For more information see [CORS middleware configuration options](https://github.com/zestedesavoir/django-cors-middleware#configuration).

Before running any manage.py command in production, make sure to export your settings file:

    export DJANGO_SETTINGS_MODULE=qabel_id.settings.production_settings

Run in production
* We recommend uwsgi emperor. See uwsgi emperor documentation: http://uwsgi-docs.readthedocs.io/en/latest/Emperor.html
* Adapt examples/uswgi-accounting.ini.example and copy it to your uwsgi emperor vassals folder.
* (Optional) use a webserver of your choice as a proxy (we recommend nginx) if you use a uwsgi UNIX socket.

## Development

To use the dummy mail backend, see: [django documentation for email](https://docs.djangoproject.com/en/1.9/topics/email/#dummy-backend)

Insert this line in qabel_id/settings/default_settings.py :

    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

In your django settings you have to set an API_SECRET that should be known only by the
qabel-block server.

# Contributing

Please refer to https://github.com/Qabel/qabel-core/blob/master/CONTRIBUTING.md
