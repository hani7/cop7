"""Add the project database to XAMPP's server list, preserving existing servers."""
from pathlib import Path

root = Path(__file__).resolve().parent.parent
config = Path('C:/xampp/phpMyAdmin/config.inc.php')
original = config.read_bytes()
marker = b'Copet portable MySQL (3308)'
if marker in original:
    print('The Copet server is already listed in phpMyAdmin.')
    raise SystemExit(0)
if b'$i' not in original or b'<?php' not in original:
    raise SystemExit('Unrecognized phpMyAdmin configuration. No changes made.')
backup = root / '.runtime' / 'phpmyadmin-config.before-mysql.php'
if backup.exists():
    raise SystemExit('A previous backup exists. Review the configuration before applying another change.')
snippet = b'''
/* Copet portable MySQL (3308) - local project database */
$i++;
$cfg['Servers'][$i]['verbose'] = 'Copet - MySQL 8.4 (3308)';
$cfg['Servers'][$i]['auth_type'] = 'cookie';
$cfg['Servers'][$i]['host'] = '127.0.0.1';
$cfg['Servers'][$i]['port'] = '3308';
$cfg['Servers'][$i]['connect_type'] = 'tcp';
$cfg['Servers'][$i]['AllowNoPassword'] = false;
$cfg['Servers'][$i]['only_db'] = 'copet';
'''
old_marker = b'/* Copet portable MariaDB (3307) - local project database */'
if old_marker in original:
    start = original.index(old_marker)
    end_line = b"$cfg['Servers'][$i]['only_db'] = 'copet';"
    end = original.index(end_line, start) + len(end_line)
    updated = original[:start] + snippet.strip() + original[end:]
elif original.rstrip().endswith(b'?>'):
    end = original.rfind(b'?>')
    updated = original[:end] + snippet + original[end:]
elif b'?>' not in original:
    updated = original + b'\n' + snippet
else:
    raise SystemExit('Unexpected PHP closing tag. No changes made.')
backup.write_bytes(original)
config.write_bytes(updated)
print('Configured Copet MySQL on port 3308 in phpMyAdmin. Original server configuration preserved and backed up.')
print('Log in using MYSQL_USER and MYSQL_PASSWORD from the project .env file.')
