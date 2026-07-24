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
	install -m 0644 pg_backup.config /etc/backups/pg_backup.config
	install -m 0755 pg_backup_rotated.sh /usr/local/sbin/pg_backup_rotated.sh
	install -m 0755 syncbackups.py /usr/local/bin/syncbackups.py
	install -m 0644 databasebackup.service /etc/systemd/system/databasebackup.service
	install -m 0644 databasebackup.timer /etc/systemd/system/databasebackup.timer
	@command -v restorecon >/dev/null 2>&1 && sudo restorecon -R /usr/local/sbin/ /etc/systemd/system/ || true

prod-enable:
	systemctl daemon-reload
	systemctl enable --now databasebackup.timer

clean:
	-rm *~
