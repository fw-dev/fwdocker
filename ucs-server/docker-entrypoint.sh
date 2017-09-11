#! /bin/bash

SUPERVISOR_BASE_PATH="/usr/local/filewave/python.v27/bin"
if [ ! -f "${SUPERVISOR_BASE_PATH}/supervisord" ]; then 
    SUPERVISOR_BASE_PATH="/usr/local/filewave/python/bin"
fi
echo $"supervisord is located in '${SUPERVISOR_BASE_PATH}''"

SUPERVISORCTL="${SUPERVISOR_BASE_PATH}/supervisorctl -c /usr/local/etc/filewave/supervisor/supervisord-server.conf"

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

FILEWAVE_BASE_DIR="/usr/local/filewave"
if [ ! "$( ls -A ${FILEWAVE_BASE_DIR}/certs)" ]; then
    echo $"Restoring filewave certs folder"
    cp -r $TEMP_DIR/certs ${FILEWAVE_BASE_DIR}
fi

if [ ! "$( ls -A ${FILEWAVE_BASE_DIR}/fwcld)" ]; then
    echo $"Restoring filewave certs folder"
    cp -r $TEMP_DIR/fwcld ${FILEWAVE_BASE_DIR}
fi

if [ ! "$(ls -A ${FILEWAVE_BASE_DIR}/apache/conf)" ]; then
    echo $"Restoring apache conf folder"
    cp -r $TEMP_DIR/conf ${FILEWAVE_BASE_DIR}/apache
fi

if [ ! "$(ls -A ${FILEWAVE_BASE_DIR}/postgres/conf)" ]; then
    echo $"Restoring postgres conf folder"
    cp -r $TEMP_DIR/postgres_conf/* ${FILEWAVE_BASE_DIR}/postgres/conf/
fi

ETC_DIR="/usr/local/etc"
if [ ! "$( ls -A ${ETC_DIR})" ]; then
    echo $"Restoring ${ETC_DIR} folder"
    cp -r $TEMP_DIR/etc/* ${ETC_DIR}

    # avoid to copy everytime supervisord scripts
    mv $TEMP_DIR/etc/filewave $TEMP_DIR/etc/filewave.bak
fi

# On a new install we need to overwrite supervisord scripts
if [ -d "$TEMP_DIR/etc/filewave" ]; then
    echo $"Installing ${ETC_DIR}/filewave folder"
    cp -r $TEMP_DIR/etc/filewave ${ETC_DIR}

    # avoid to copy everytime supervisord scripts
    mv $TEMP_DIR/etc/filewave $TEMP_DIR/etc/filewave.bak
fi

FILEWAVE_TMP_DIR="${FILEWAVE_BASE_DIR}/tmp"
if [ -f "$FILEWAVE_TMP_DIR/settings_custom.py" ]; then
    echo $"Restoring settings_custom file"
    cp -r $FILEWAVE_TMP_DIR/settings_custom.py ${FILEWAVE_BASE_DIR}/django/filewave

    # Avoid to restore everytime we start
    mv $FILEWAVE_TMP_DIR/settings_custom.py $FILEWAVE_TMP_DIR/settings_custom.py.bak
fi

echo $"Restoring owners for file/folders"
chown root:apache ${FILEWAVE_BASE_DIR}/apache/passwd
chown apache:apache ${FILEWAVE_BASE_DIR}/certs ${FILEWAVE_BASE_DIR}/certs/server.* ${FILEWAVE_BASE_DIR}/ipa ${FILEWAVE_BASE_DIR}/media ${FILEWAVE_BASE_DIR}/apache/conf ${FILEWAVE_BASE_DIR}/apache/conf/*
chown postgres:daemon ${FILEWAVE_BASE_DIR}/certs/postgres.*

# Remove garbage from previous execution
rm -f /usr/local/filewave/apache/logs/*pid /fwxserver/DB/pg_data/*.pid

# Upgrade the cluster DB (if needed) and run migrations
/usr/local/filewave/python/bin/python -m fwcontrol.postgres init_or_upgrade_db_folder

# The previous command initialize django, so the owner of the log files has to be changed here
chown -R apache:apache ${FILEWAVE_BASE_DIR}/fwcld ${FILEWAVE_BASE_DIR}/log

# for supervisord to always expand the environment variables. See /usr/local/etc/filewave/supervisor/supervisord-server.conf
export http_proxy=""
export https_proxy=""
export no_proxy=""
. /etc/environment

# Run Supervisord in daemon mode
${SUPERVISOR_BASE_PATH}/supervisord -c /usr/local/etc/filewave/supervisor/supervisord-server.conf

echo "Supervisord is running"

# wait forever
while true
do
  tail -f /dev/null & wait ${!}
done

