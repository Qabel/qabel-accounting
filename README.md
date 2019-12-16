<img align="left" width="0" height="150px" hspace="20"/>
<a href="https://qabel.de" align="left">
	<img src="https://files.qabel.de/img/qabel_logo_orange_preview.png" height="150px" align="left"/>
</a>
<img align="left" width="0" height="150px" hspace="25"/>
# The Qabel Accounting Server


This project provides the accounting server for <a href="https://qabel.de"><img alt="Qabel" src="https://files.qabel.de/img/qabel-kl.png" height="18px"/></a> that manages Qabel-Accounts that authorize Qabel Box usage according to the [Qabel Box Protocol](http://qabel.github.io/docs/Qabel-Protocol-Box/).

## Introduction
For a comprehensive documentation of the whole Qabel Platform use https://qabel.de as the main source of information. http://qabel.github.io/docs/ may provide additional technical information.

Qabel consists of multiple Projects:
 * [Qabel Android Client](https://github.com/Qabel/qabel-android)
 * [Qabel Desktop Client](https://github.com/Qabel/qabel-desktop)
 * [Qabel Core](https://github.com/Qabel/qabel-core) is a library that includes the common code between both clients to keep them consistent
 * [Qabel Drop Server](https://github.com/Qabel/qabel-drop) is the target server for drop messages according to the [Qabel Drop Protocol](http://qabel.github.io/docs/Qabel-Protocol-Drop/)
 * [Qabel Accounting Server](https://github.com/Qabel/qabel-accounting) manages Qabel-Accounts that authorize Qabel Box usage according to the [Qabel Box Protocol](http://qabel.github.io/docs/Qabel-Protocol-Box/)
 * [Qabel Block Server](https://github.com/Qabel/qabel-block) serves as the storage backend according to the [Qabel Box Protocol](http://qabel.github.io/docs/Qabel-Protocol-Box/)

## Requirements
* Docker
* Docker-Compose

##  Bootstrap the Project for development

	    $ git clone git@git.qabel.de/Qabel/accounting-cookiecutter.git
	    to build run
        $ docker-compose -f local.yml build
	    to run it
        $ docker-compose -f local.yml up
        to run tests
        $ docker-compose -f local.yml -f testing.yml up --exit-code-from django --abort-on-container-exit django

## <a name="production_setup"></a>Production setup


The server exports [prometheus](https://www.prometheus.io) metrics at /metrics. If those should not be public, you should
block this location in the webserver.

If you have problems with CORS (Cross-Origin Resource Sharing), edit the 'CORS_ORIGIN_WHITELIST' in the
configuration. For more information see [CORS middleware configuration options](https://github
.com/zestedesavoir/django-cors-middleware#configuration).

## Development

To use the dummy mail backend, see: [django documentation for email](https://docs.djangoproject.com/en/1.9/topics/email/#dummy-backend)

Insert this line in config/settings/default_settings.py :

    EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

In your django settings you have to set an API_SECRET that should be known only by the
qabel-block server.


# Contributing

Please refer to https://github.com/Qabel/qabel-core/blob/master/CONTRIBUTING.md
