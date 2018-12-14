all:

prod:
	scp pg_backup.config pg_backup_rotated.sh backups@falcon:
	scp pg_backup.config pg_backup_rotated.sh backups@localhost:
