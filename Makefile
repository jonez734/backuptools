PROJECT = backuptools

.PHONY: all deploy deploy-www deploy-tui prod clean

all:

deploy: deploy-tui deploy-www

deploy-tui:
	python -m build --outdir dist/

deploy-www:
	@echo "deploy-www: not yet implemented"

prod:
	rsync -av pg_backup.config /etc/backups/pg_backup.config
	rsync -av pg_backup_rotated.sh /usr/local/sbin/pg_backup_rotated.sh
	rsync -av syncbackups.py /usr/local/bin/syncbackups.py

clean:
	-rm *~
