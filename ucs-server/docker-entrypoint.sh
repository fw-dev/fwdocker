#!/usr/bin/env bash

# first time? empty? you bind-mounted the damn directory - how dare you!
if [ ! -d "/fwxserver/DB" ]; then
   cp -r /usr/local/filewave/tmp/fwxserver/DB /fwxserver/
fi

if [ ! -d "/fwxserver/Data Folder" ]; then
   cp -r /usr/local/filewave/tmp/fwxserver/"Data Folder" /fwxserver/
fi

if [ ! -d "/usr/local/filewave/certs" ]; then
   cp -r /usr/local/filewave/tmp/certs /usr/local/filewave/
fi

if [ ! -d "/usr/local/filewave/apache/conf" ]; then
   cp -r /usr/local/filewave/tmp/conf /usr/local/filewave/apache
fi

/usr/local/filewave/python.v27/bin/supervisord -n -c /usr/local/etc/filewave/supervisor/supervisord-server.conf

