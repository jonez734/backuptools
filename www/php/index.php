<?php

require_once('/srv/www/bbsengine6/php/bootstrap.php');

require_once("config.php");

require_once("engine.php");
require_once("session.php");
require_once("database.php");

require_once("zoid6.php");

class index
{
  function main()
  {
    \bbsengine6\session\start();

    \bbsengine6\setcurrentsite(\config\SITENAME);
    \bbsengine6\setcurrentpage("index");
    \bbsengine6\setcurrentaction("index");
    \bbsengine6\setreturnto(SITEURL);

    $modes = [
      [
        "name" => "Full Backup",
        "command" => "backup empyre",
        "description" => "Copies from source to staging, then staging to backup device. The default mode when no flags are specified.",
      ],
      [
        "name" => "Stage-only",
        "command" => "backup empyre --stage-only",
        "description" => "Only copies source projects to the staging directory. Skips the backup device sync.",
      ],
      [
        "name" => "Thumb-only",
        "command" => "backup empyre --thumb-only",
        "description" => "Only syncs staging to the backup device. Useful when staging already exists from a previous stage-only run.",
      ],
      [
        "name" => "Database Backup",
        "command" => "backup database",
        "description" => "Syncs PostgreSQL dumps from /srv/backups/database directly to the backup device. Also accepts 'minotaur' as an alias.",
      ],
    ];

    $options = [
      ["flag" => "--staging PATH", "description" => "Staging directory (default: /srv/backups/)"],
      ["flag" => "--backupdevice PATH", "description" => "Backup device path (default: $BACKUPDEVICE)"],
      ["flag" => "--excludes FILE", "description" => "rsync excludes file"],
      ["flag" => "--dry-run", "description" => "Show what would be done without making changes"],
      ["flag" => "--verbose", "description" => "Verbose output"],
      ["flag" => "--no-mount-check", "description" => "Skip mount point check for backup device"],
      ["flag" => "--stage-only", "description" => "Only copy to staging, skip backup device sync"],
      ["flag" => "--thumb-only", "description" => "Only sync staging to backup device"],
      ["flag" => "--database-source PATH", "description" => "Source path for database backups"],
    ];

    $systemd = [
      [
        "name" => "databasebackup.timer",
        "description" => "Triggers databasebackup.service 5 minutes after boot, then every hour.",
      ],
      [
        "name" => "databasebackup.service",
        "description" => "Runs pg_backup_rotated.sh as the backups user to perform rotated PostgreSQL backups (daily, weekly, monthly).",
      ],
      [
        "name" => "syncbackups.timer",
        "description" => "Triggers syncbackups.service 5 minutes after boot, then every hour.",
      ],
      [
        "name" => "syncbackups.service",
        "description" => "Runs the legacy syncbackups script for rsync-based project syncing.",
      ],
    ];

    $data = [];
    $data["modes"] = $modes;
    $data["options"] = $options;
    $data["systemd"] = $systemd;
    $data["choices"] = \zoid6\buildchoices([]);
    \bbsengine6\displaypage($data, "index.tmpl");

    return;
  }
};

$a = new index();
$a->main();

?>
