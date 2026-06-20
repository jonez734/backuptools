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

## Environment

- `BACKUPDEVICE` - Override default backup device path

## Development

```bash
# Run without installing
PYTHONPATH=/home/opencode/data/work/backuptools/src python -m backuptools empyre

# Run tests
cd backuptools/src
python -m pytest tests/
```

## See Also

- `backuptools.spec` - Detailed specification
- `bbsengine6/module.spec` - Module ABI documentation
