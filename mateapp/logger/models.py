from django.db import models
from django.utils import timezone

class LogEntry(models.Model):
    timestamp = models.DateTimeField(default=timezone.now)
    level = models.CharField(max_length=20)
    message = models.TextField()

    def __str__(self):
        return f"[{self.timestamp}] {self.level} - {self.message}"
    
    class Meta:
        verbose_name_plural = "Log entries"