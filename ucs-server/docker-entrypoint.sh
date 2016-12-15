#! /bin/bash

SUPERVISORCTL='/usr/local/filewave/python.v27/bin/supervisorctl -c /usr/local/etc/filewave/supervisor/supervisord-server.conf'

# SIGTERM-handler
term_handler() {
  pid=$($SUPERVISORCTL pid)
  if [ $pid -ne 0 ]; then
    echo "Stopping all processes..."
    $SUPERVISORCTL stop all

    echo "Stopping supervisord..."
    kill -SIGTERM "$pid"

    sleep 1
  fi
  echo "Done"
  exit 0; # 128 + 15 -- SIGTERM
}

# setup handlers
# on callback, kill the last background process, which is `tail -f /dev/null` and execute the specified handler
trap 'kill ${!}; term_handler' SIGTERM


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

# Remove garbage from previous execution
rm -f /usr/local/filewave/apache/logs/*pid /fwxserver/DB/pg_data/*.pid

# Upgrade the cluster DB (if needed) and run migrations
/usr/local/filewave/python/bin/python -m fwcontrol.postgres init_or_upgrade_db_folder

# Run Supervisord in daemon mode
/usr/local/filewave/python.v27/bin/supervisord -c /usr/local/etc/filewave/supervisor/supervisord-server.conf

echo "Supervisord is running"

# wait forever
while true
do
  tail -f /dev/null & wait ${!}
done

