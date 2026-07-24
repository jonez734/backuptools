PROJECT = backuptools

.PHONY: all deploy deploy-www deploy-tui prod prod-enable clean

all:

deploy: deploy-tui deploy-www

deploy-tui:
	python -m build --outdir dist/

deploy-www:
	@echo "deploy-www: not yet implemented"

prod:
	mkdir -p /etc/backups
	mkdir -p /srv/backups/database
	rsync -av pg_backup.config /etc/backups/pg_backup.config
	rsync -av pg_backup_rotated.sh /usr/local/sbin/pg_backup_rotated.sh
	rsync -av syncbackups.py /usr/local/bin/syncbackups.py
	rsync -av databasebackup.service /etc/systemd/system/databasebackup.service
	rsync -av databasebackup.timer /etc/systemd/system/databasebackup.timer

prod-enable:
	systemctl daemon-reload
	systemctl enable --now databasebackup.timer

clean:
	-rm *~
