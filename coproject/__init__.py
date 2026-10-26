"""Project package initialization."""

import pymysql

# Django 6.1 checks the MySQLdb compatibility version. PyMySQL exposes the
# legacy MySQLdb-compatible version by default, so advertise the compatible
# API level before installing the adapter.
pymysql.version_info = (2, 2, 1)
pymysql.install_as_MySQLdb()
