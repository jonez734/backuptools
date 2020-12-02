import os
import ttyio4 as ttyio
import bbsengine4 as bbsengine
from dateutil.tz import tzlocal
from datetime import datetime
from time import strftime

t = datetime.now(tzlocal())

# pg_dump -Fc zoidbo > zoidbo-cyclops-`datestamp`.pgdump
datestamp = bbsengine.datestamp(t, format="%Y%m%d%H%M")
ttyio.echo("datestamp=%s" % (datestamp))
os.system("pg_dump -Fc zoidbo > /srv/backups/cyclops/zoidbo-cyclops-%s.pgdump" % (datestamp))
os.system("pg_dump -Fc zoidweb4 > /srv/backups/cyclops/zoidweb4-cyclops-%s.pgdump" % (datestamp))
