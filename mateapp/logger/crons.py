from django_cron import CronJobBase, Schedule
import logging
import datetime
from .models import LogEntry
from django.conf import settings

logger = logging.getLogger('logfile')

class RemoveOldLogs(CronJobBase):
    '''Remove older log files'''

    # run every 24 hs.
    RUN_EVERY_MINS = 1440

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'Remove old log entries'

    def do(self):
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=settings.LOG_RETENTION_DAYS)
        old_logs = LogEntry.objects.filter(timestamp__lt=cutoff_date)
        count = old_logs.count()
        old_logs.delete()
        logger.info(f'Deleted {count} log enries older than {settings.LOG_RETENTION_DAYS} days.')