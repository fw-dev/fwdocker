#!/usr/bin/env python

import os, pwd
LOG_FILE="/private/var/log/fw_backup.log"

def get_username():
    return pwd.getpwuid( os.getuid() )[ 0 ]

print get_username()