# backuptools

A set of Python scripts to make backups using rsync. Conforms to bbsengine6 module ABI.

## Quick Start

```bash
# Install
pip install -e backuptools/src/

# Backup a project
backup empyre

# Backup multiple projects
backup empyre teos asimov
```

## Modes

### Full Backup (default)
Copies from source to staging, then staging to backup device.

### Stage-only
```bash
backup empyre --stage-only
```
Only copies to staging, skips backup device.

### Thumb-only
```bash
backup empyre --thumb-only
```
Only syncs staging to backup device. Useful when staging already exists.

Note: The rsync from staging to thumbdrive syncs the entire `work/` directory, not just the specified project(s).

### Database Backup
```bash
backup database
backup minotaur
```
Syncs database dumps from `/srv/backups/database` directly to the backup device. Skips the staging step since the pg_dumps are already staged locally by the databasebackup timer. Both `database` and `minotaur` are aliases for the same source.

```bash
backup database --dry-run
backup database --database-source /srv/backups/database
```

Note: `--stage-only` has no effect in database mode (staging is always skipped).

## Options

| Option | Description |
|--------|-------------|
| `--staging PATH` | Staging directory (default: /srv/backups/) |
| `--backupdevice PATH` | Backup device path (default: $BACKUPDEVICE or /run/media/jam/BEA6-BBCE/) |
| `--excludes FILE` | rsync excludes file |
| `--dry-run` | Show what would be done |
| `--verbose` | Verbose output |
| `--no-mount-check` | Skip mount check (for testing) |
| `--stage-only` | Only copy to staging |
| `--thumb-only` | Only sync staging to backup device |
| `--database-source PATH` | Source path for database backups (default: /srv/backups/database) |

## Environment

- `BACKUPDEVICE` - Override default backup device path

## Development

```bash
# Run without installing
PYTHONPATH=/home/opencode/data/work/backuptools/src python -m backuptools empyre

# Run tests (requires Python 3.12)
cd backuptools/src
python3.12 -m pytest tests/

# Run unit tests only
python3.12 -m pytest tests/ -m unit
```

## Deployment

### Systemd Units

`databasebackup.service` and `databasebackup.timer` are bundled as package data in the wheel. The timer triggers the service 5 minutes after boot and then every hour.

### Makefile Targets

```bash
# Install all files to system paths (requires root)
sudo make prod

# Enable and start the databasebackup timer
sudo make prod-enable
```

The `prod` target:
- Creates the `backups` system user if it doesn't exist
- Adds the calling user to the `backups` group
- Installs files with restricted permissions (group-readable, no world access)
- Creates `/etc/backups` and `/srv/backups/database` directories
- Runs `restorecon` on SELinux systems

### Wheel Install

The `.service` and `.timer` files are included in the wheel as package data. After `pip install`, they can be found at:
```
<site-packages>/backuptools/databasebackup.service
<site-packages>/backuptools/databasebackup.timer
```

## See Also

- `backuptools.spec` - Detailed specification
- `bbsengine6/module.spec` - Module ABI documentation
