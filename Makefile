PROJECT = backuptools

.PHONY: all deploy deploy-www deploy-tui prod prod-enable clean

all:

deploy: deploy-tui deploy-www

deploy-tui:
	python -m build --outdir dist/

deploy-www:
	@echo "deploy-www: not yet implemented"

prod:
	install -d /etc/backups
	install -d /srv/backups/database
	id backups >/dev/null 2>&1 || useradd -r -s /sbin/nologin backups
	usermod -aG backups jam
	install -d -m 0750 -o backups -g backups /etc/backups
	install -d -m 0750 -o backups -g backups /srv/backups/database
	install -m 0640 -o backups -g backups pg_backup.config /etc/backups/pg_backup.config
	install -m 0750 pg_backup_rotated.sh /usr/local/sbin/pg_backup_rotated.sh
	install -m 0750 syncbackups.py /usr/local/bin/syncbackups.py
	install -m 0640 databasebackup.service /etc/systemd/system/databasebackup.service
	install -m 0640 databasebackup.timer /etc/systemd/system/databasebackup.timer
	@command -v restorecon >/dev/null 2>&1 && sudo restorecon -R /usr/local/sbin/ /etc/systemd/system/ /srv/backups/ || true

prod-enable:
	systemctl daemon-reload
	systemctl enable --now databasebackup.timer

clean:
	-rm *~
