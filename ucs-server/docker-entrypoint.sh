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
    echo $"Restoring apache conf folder"
   cp -r $TEMP_DIR/conf /usr/local/filewave/apache
fi

if [ ! "$(ls -A /usr/local/filewave/postgres/conf)" ]; then
    echo $"Restoring postgres conf folder"
   cp -r $TEMP_DIR/postgres_conf/* /usr/local/filewave/postgres/conf/
fi

# Upgrade the cluster DB (if needed) and run migrations
/usr/local/filewave/python/bin/python -m fwcontrol.postgres init_or_upgrade_db_folder

/usr/local/filewave/python.v27/bin/supervisord -n -c /usr/local/etc/filewave/supervisor/supervisord-server.conf

