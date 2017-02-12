#!/bin/sh
source activate.sh
inv deploy
uwsgi deployed/current/uwsgi.ini
