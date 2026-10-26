"""Provision portable MySQL; preserve the previous server and its data."""
import configparser
import os
from pathlib import Path
import secrets
import shutil

import MySQLdb
from dotenv import dotenv_values, set_key


ROOT = Path(__file__).resolve().parent.parent
RUNTIME = ROOT / '.runtime'
ENV = ROOT / '.env'
ADMIN_CONFIG = RUNTIME / 'mysql-admin.cnf'
APP_SECRET = RUNTIME / 'mysql-app-password.txt'


def main():
    original = dotenv_values(ENV)
    if original.get('MYSQL_PORT', '3306') != '3308':
        # Switching an existing app with data requires an explicit data migration.
        old = MySQLdb.connect(
            host=original.get('MYSQL_HOST', '127.0.0.1'), port=int(original.get('MYSQL_PORT', '3306')),
            user=original.get('MYSQL_USER', 'root'), passwd=original.get('MYSQL_PASSWORD', ''),
            db=original.get('MYSQL_DATABASE', 'copet'), connect_timeout=5,
        )
        with old.cursor() as cursor:
            cursor.execute('SHOW TABLES')
            tables = [row[0] for row in cursor.fetchall()]
            for table in tables:
                if table in ['django_migrations', 'django_content_type', 'auth_permission']:
                    continue
                if not (table.startswith('eliteapp_') or table in ['auth_group', 'auth_group_permissions', 'django_session', 'django_admin_log']):
                    raise RuntimeError('Unexpected source tables. Migrate their schema and data before switching servers.')
                quoted = table.replace('`', '``')
                cursor.execute(f'SELECT COUNT(*) FROM `{quoted}`')
                if cursor.fetchone()[0]:
                    raise RuntimeError('The source contains application data. Migrate it before switching servers.')
        old.close()
        backup = RUNTIME / 'env.before-mysql'
        if not backup.exists():
            shutil.copyfile(ENV, backup)

    root_password = ''
    if ADMIN_CONFIG.exists():
        parser = configparser.ConfigParser(interpolation=None)
        parser.read(ADMIN_CONFIG, encoding='utf-8')
        root_password = parser['client']['password']
    try:
        connection = MySQLdb.connect(host='127.0.0.1', port=3308, user='root', passwd=root_password, connect_timeout=5)
    except MySQLdb.OperationalError as exc:
        if not root_password or exc.args[0] != 1045:
            raise
        # Recover only the window between writing admin.cnf and setting the password.
        connection = MySQLdb.connect(host='127.0.0.1', port=3308, user='root', passwd='', connect_timeout=5)

    with connection.cursor() as cursor:
        cursor.execute('SELECT @@datadir, VERSION(), @@version_comment')
        datadir, version, vendor = cursor.fetchone()
        if Path(datadir).resolve() != (RUNTIME / 'mysql-data').resolve():
            raise RuntimeError('Port 3308 belongs to a different server. No changes made.')
        if not version.startswith('8.4.') or 'MySQL' not in vendor:
            raise RuntimeError('Expected MySQL Community Server 8.4. No changes made.')

        if not APP_SECRET.exists():
            APP_SECRET.write_text(secrets.token_urlsafe(36), encoding='utf-8')
        app_password = APP_SECRET.read_text(encoding='utf-8')
        cursor.execute('CREATE DATABASE IF NOT EXISTS copet CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
        for host in ['localhost', '127.0.0.1']:
            cursor.execute('CREATE USER IF NOT EXISTS %s@%s IDENTIFIED BY %s', ('copet_app', host, app_password))
            cursor.execute('ALTER USER %s@%s IDENTIFIED BY %s', ('copet_app', host, app_password))
            cursor.execute('GRANT ALL PRIVILEGES ON copet.* TO %s@%s', ('copet_app', host))

        if not root_password:
            root_password = secrets.token_urlsafe(36)
        ADMIN_CONFIG.write_text(
            '[client]\nhost=127.0.0.1\nport=3308\nuser=root\npassword=' + root_password + '\n', encoding='utf-8',
        )
        cursor.execute("SELECT Host FROM mysql.user WHERE User='root'")
        for (host,) in cursor.fetchall():
            cursor.execute('ALTER USER %s@%s IDENTIFIED BY %s', ('root', host, root_password))
    connection.close()

    # Verify the least-privileged application account before changing Django's config.
    probe = MySQLdb.connect(host='127.0.0.1', port=3308, user='copet_app', passwd=app_password, db='copet')
    probe.close()
    pending = RUNTIME / 'env.pending'
    shutil.copyfile(ENV, pending)
    for key, value in {'MYSQL_DATABASE': 'copet', 'MYSQL_HOST': '127.0.0.1', 'MYSQL_PORT': '3308',
                       'MYSQL_USER': 'copet_app', 'MYSQL_PASSWORD': app_password}.items():
        set_key(pending, key, value)
    os.replace(pending, ENV)
    print(f'Django configured for copet on {vendor} {version}, port 3308.')
    print('Local passwords generated without display. Previous servers and data were preserved.')


if __name__ == '__main__':
    main()
