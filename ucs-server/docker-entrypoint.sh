#!/usr/bin/env bash

# first time? empty? you bind-mounted the damn directory - how dare you!
#if [ ! -d "/fwxserver/DB/pg_data" ]; then
#    cp -r /usr/local/filewave/tmp/pg_data /fwxserver/DB/
#fi

/usr/local/filewave/python.v27/bin/supervisord -n -c /usr/local/etc/filewave/supervisor/supervisord-server.conf

