# backuptools

## Overview
backuptools - A set of Python scripts to make backups using rsync. Conforms to bbsengine6 module ABI.

## Project Structure
```
backuptools/
├── bin/
│   └── backup                    # bash script wrapper
├── src/
│   ├── backuptools/
│   │   ├── __init__.py           # Package entry - delegates to lib.runmodule()
│   │   ├── __main__.py           # CLI entry - parses args, calls lib.runmodule()
│   │   ├── lib.py                # Constants, helpers, buildargs(), runmodule()
│   │   ├── main.py               # Main module logic
│   │   ├── _version.py           # Version info
│   │   └── rsync-excludes.txt    # rsync exclude patterns (package data)
│   └── pyproject.toml            # Package config
└── backuptools.spec              # This file
```

## bbsengine6 Module ABI

backuptools conforms to the bbsengine6 module ABI (see `bbsengine6/module.spec`).

### Package Entry (__init__.py)
```python
from . import lib

def init(args, **kwargs) -> bool:
    return True

def access(args, op, **kwargs) -> bool:
    return True

def buildargs(args=None, **kwargs):
    return None

def main(args, **kwargs):
    return lib.runmodule(args, "main", **kwargs)
```

### lib.py
Provides `PACKAGENAME`, `buildargs()`, `runmodule()`, and helper functions.

### main.py
Contains the actual backup logic: `init()`, `access()`, `buildargs()`, `main()`.

## CLI: backup

### Usage
```
backup <project> [project ...] [options]
```

### Arguments
- `projects` - Project names to backup (space-separated, required)

### Options
- `--debug` - Debug mode
- `--staging STAGING` - Staging directory base (default: /srv/backups/)
- `--backupdevice PATH` - Backup device path (default: $BACKUPDEVICE or /run/media/jam/BEA6-BBCE/)
- `--excludes FILE` - rsync excludes file (default: package data)
- `--dry-run` - Dry run mode
- `--verbose` - Verbose output
- `--no-mount-check` - Skip mount point check (for testing)
- `--stage-only` - Only copy to staging, skip backup device sync
- `--thumb-only` - Only sync staging to backup device, skip source to staging
- `--database-source PATH` - Source path for database backups (default: /srv/backups/minotaur)

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

### Database backup (`backup database` or `backup minotaur`)
1. Validate excludes file is readable
2. Validate database source exists: /srv/backups/minotaur
3. Validate backup device mounted and writable
4. rsync /srv/backups/minotaur → <backupdevice>/

No staging step — the pg_dumps are already staged locally by the databasebackup timer.

Aliases `database` and `minotaur` are matched by `DATABASE_RE` (re.compile `r"^(database|minotaur)$"`). Both rsync the same default source (`/srv/backups/minotaur`). Override with `--database-source`.

### Stage-only mode (--stage-only)
- Skip steps 3 and 4 (exit after step 2)

### Thumb-only mode (--thumb-only)
- Skip source to staging (step 2)
- Only do staging to backup device (steps 3-4)
- Useful when staging already exists from previous run

## Running

### Installed
```bash
backup empyre
```

### Development (no install)
```bash
PYTHONPATH=/home/opencode/data/work/backuptools/src python -m backuptools empyre
```

### Via bbsengine6.module.run()
```python
from bbsengine6 import module
module.run(args, "backuptools")
```

## Constants (lib.py)
- `PACKAGENAME = "backuptools"`
- `DEFAULT_EXCLUDES` - Path to rsync-excludes.txt
- `DEFAULT_STAGING = "/srv/backups/"`
- `DEFAULT_BACKUPDEVICE = "/run/media/jam/BEA6-BBCE/"`
- `DEFAULT_DATABASE_SOURCE = "/srv/backups/minotaur"`
- `DATABASE_RE = re.compile(r"^(database|minotaur)$")` - Aliases for database backup
- `SOURCE_BASE = "/home/opencode/data/work"`

## Dependencies
- bbsengine6
- rsync (system binary)

## Testing

```bash
cd src
python3.12 -m pytest tests/

# Run unit tests only
python3.12 -m pytest tests/ -m unit
```

### Test Markers
- `unit` - Unit tests (registered in pyproject.toml)

## pyproject.toml

Key configuration:
```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
]
```
