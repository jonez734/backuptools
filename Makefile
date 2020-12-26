all:

prod:
	scp pg_backup.config pg_backup_rotated.sh backups@falcon:
	scp syncbackups.py /usr/local/bin/
	scp backupdatabase /usr/local/bin/
clean:
	-rm *~
