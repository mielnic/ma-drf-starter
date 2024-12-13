from django.contrib import admin
from .models import LogEntry
from django.db.models import Q
from unfold.admin import ModelAdmin

@admin.register(LogEntry)
class LogEntryAdmin(ModelAdmin):
    list_display = ('timestamp', 'level', 'message')
    search_fields = ('level', 'message')
    readonly_fields = ('timestamp', 'level', 'message')

    def get_search_results(self, request, queryset, search_term):
        use_distinct = False
        query = Q()

        if search_term.startswith('!'):
            # If search term starts with '!', perform exclusion search
            search_term = search_term[1:]  # Remove '!'
            for field in self.search_fields:
                query &= ~Q(**{f"{field}__icontains": search_term})
        else:
            # Perform standard search
            for field in self.search_fields:
                query |= Q(**{f"{field}__icontains": search_term})

        queryset = queryset.filter(query)
        return queryset, use_distinct

    def has_add_permission(self, request):
        return False  # Disables the ability to add log entries manually through the admin

    def has_change_permission(self, request, obj=None):
        return False  # Disables the ability to edit log entries through the admin