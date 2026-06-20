# backuptools

## Overview
backuptools - A set of Python scripts to make backups using rsync.

## Project Structure
```
backuptools/
├── bin/
│   └── backup                    # bash script wrapper
├── src/
│   ├── backuptools/
│   │   ├── __init__.py           # Main backup module
│   │   ├── _version.py            # Version info
│   │   └── rsync-excludes.txt    # rsync exclude patterns
│   └── pyproject.toml            # Package config
└── backuptools.spec              # This file
```

## CLI: backup

### Usage
```
backup <project> [project ...] [options]
```

### Arguments
- `projects` - Project names to backup (space-separated, required)

### Options
- `--staging STAGING` - Staging directory base (default: /srv/backups/)
- `--backupdevice PATH` - Backup device path (default: $BACKUPDEVICE or /run/media/jam/BEA6-BBCE/)
- `--excludes FILE` - rsync excludes file (default: package data)
- `--dry-run` - Dry run mode
- `--verbose` - Verbose output
- `--no-mount-check` - Skip mount point check (for testing)
- `--stage-only` - Only copy to staging, skip backup device sync

### Environment
- `BACKUPDEVICE` - Override default backup device path

## Flow

### Full backup (default)
1. Validate excludes file is readable
2. For each project:
   a. Validate source exists: /home/opencode/data/work/<project>
   b. Create/validate staging dir: <staging>/work/<project>/
   c. rsync /home/opencode/data/work/<project> → <staging>/work/
3. Validate backup device mounted and writable
4. rsync <staging>/work/ → <backupdevice>/work/

### Stage-only mode (--stage-only)
- Skip steps 3 and 4 (exit after step 2)

## Example
```bash
# Backup single project
backup empyre

# Backup multiple projects
backup empyre teos asimov

# Dry run
backup empyre --dry-run

# Stage only (for later manual sync)
backup empyre --stage-only

# Custom staging and backup device
backup empyre --staging /tmp/staging/ --backupdevice /media/backup/
```

## bbsengine6 Module ABI
backuptools conforms to the bbsengine6 module ABI:
- `init(args, **kwargs) -> bool`
- `access(args, op, **kwargs) -> bool`
- `buildargs(args=None, **kwargs) -> ArgumentParser`
- `main(args, **kwargs) -> int`

Can be run via `bbsengine6.module.run(args, "backuptools.backup")`

## Dependencies
- bbsengine6 (for io module)
- rsync (system binary)
