#!/usr/bin/env bash

set -ex
# As in worker, we need inject environment setup
# TODO: get rid of this
DIR=$(dirname "${BASH_SOURCE[0]}")
source $DIR/env.sh

f8a-webapp.py initjobs

cd /usr/bin
exec uwsgi --http 0.0.0.0:35000 -p 1 -w f8a-webapp --enable-threads
