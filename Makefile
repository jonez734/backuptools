export PROJECT = backuptools
export STAGE = /srv/www/vhosts/zoidtechnologies.com/html/$(PROJECT)/
export SKINDIR = $(STAGE)skin/
export HOST = merlin

export SCSSLOADPATH = --load-path /home/opencode/data/work/zoid6/shared/skin/scss/ \
	--load-path /home/opencode/data/work/bbsengine6/skin/scss/ \
	--load-path /home/opencode/data/work/backuptools/www/skin/scss/
export SCSS = sass $(SCSSLOADPATH) --sourcemap=none --stop-on-error --trace --style expanded

export RSYNC = rsync --chmod=Dg=rwxs,Fgu=rw,Fo=r --no-times --verbose \
	--archive --update --backup --recursive \
	--human-readable --checksum --rsh=ssh \
	--mkpath --exclude='*~'

.PHONY: all deploy deploy-www deploy-tui version prod prod-enable clean

all:

deploy: deploy-tui deploy-www

version:
	$(MAKE) -C src version

deploy-tui: version
	$(MAKE) -C src build

deploy-www:
	$(MAKE) -C www prod
	$(RSYNC) $(STAGE) $(HOST):$(STAGE)

prod:
	install -d /etc/backups
	install -d /srv/backups/database
	id backups >/dev/null 2>&1 || useradd -r -s /sbin/nologin backups
	usermod -aG backups $(shell whoami)
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
