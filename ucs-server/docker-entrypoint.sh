#! /bin/bash

echo $"Entry point"

TEMP_DIR="/tmp/filewave"
if [ ! "$(ls -A /fwxserver/DB)" ]; then
    echo $"Restoring DB folder"
    cp -r $TEMP_DIR/DB /fwxserver/

    chown -R postgres:wheel /fwxserver/DB/pg_data
fi

DATA_FOLDER="Data Folder"
if [ ! -d "/fwxserver/Data Folder" ]; then
    echo $"Restoring Data Folder"
   cp -r $TEMP_DIR/$DATA_FOLDER /fwxserver/
fi

if [ ! "$( ls -A /usr/local/filewave/certs)" ]; then
    echo $"Restoring filewave certs folder"
   cp -r $TEMP_DIR/certs /usr/local/filewave/
fi

if [ ! "$(ls -A /usr/local/filewave/apache/conf)" ]; then
    echo $"Restoring apache conf older"
   cp -r $TEMP_DIR/conf /usr/local/filewave/apache
fi

/usr/local/filewave/python.v27/bin/supervisord -n -c /usr/local/etc/filewave/supervisor/supervisord-server.conf

