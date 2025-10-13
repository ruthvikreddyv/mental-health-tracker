from django.contrib import admin
from .models import Assessment, JournalEntry, MentalHealthResponse

admin.site.register(Assessment)
admin.site.register(JournalEntry)
admin.site.register(MentalHealthResponse)
