import logging
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from logger.models import LogEntry

logger = logging.getLogger('logfile')

class Command(BaseCommand):
    help = 'Removes log entries older than a certain number of days as defined in settings.LOG_RETENTION_DAYS'

    def handle(self, *args, **kwargs):
        try:
            cutoff_date = datetime.datetime.now() - datetime.timedelta(days=settings.LOG_RETENTION_DAYS)
            old_logs = LogEntry.objects.filter(timestamp__lt=cutoff_date)
            count = old_logs.count()
            old_logs.delete()
            logger.info(f'Deleted {count} log entries older than {settings.LOG_RETENTION_DAYS} days.')
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old log entries.'))
        except Exception as ex:
            logger.error(f"An error occurred while deleting old log entries: {str(ex)}")
            self.stderr.write(self.style.ERROR(f'Error: {str(ex)}'))
